import os
import shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from redis import Redis
from rq import Queue
from tasks import process_tts, UPLOAD_DIR, EXPORT_DIR
from utils import generate_code, check_filetype, TTSRequest
import re as regex

api = FastAPI()
redis_conn = Redis(host="localhost", port=6379)
task_queue = Queue("default", connection=redis_conn)

# Controlled static mount — only ever serves files under EXPORT_DIR,
# and FastAPI's StaticFiles resolves paths safely (no ../ escapes).
api.mount("/files", StaticFiles(directory=EXPORT_DIR), name="files")


# 2. Updated Endpoint
@api.post("/tts/")
async def generate_tts(request: TTSRequest):
    code = generate_code()

    
    # Pass the text string directly to the queue
    job = task_queue.enqueue(process_tts, code, request.text, request.voice, job_id=code)
    
    return {"job_id": job.id, "status": "Queued"}


@api.get("/status/{job_id}")
def check_status(job_id: str):
    job = task_queue.fetch_job(job_id)
    if not job:
        return {"error": "Invalid job ID"}
    return {"status": job.get_status(), "result": job.result}