import os
import logging
from kittentts import KittenTTS

logger = logging.getLogger("uvicorn")

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s:     %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

UPLOAD_DIR = "/tmp/asep/uploads"
EXPORT_DIR = "/tmp/asep/exports"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

# Initialize TTS model globally to avoid reloading on every request
logger.info("Loading KittenTTS model...")
tts_model = KittenTTS("KittenML/kitten-tts-mini-0.8")
logger.info("KittenTTS model loaded.")


# 3. Updated Background Task
def process_tts(code: str, text: str, voice: str = "Bruno"):
    export_path = os.path.join(EXPORT_DIR, code)
    os.makedirs(export_path, exist_ok=True)

    logger.info(f"[{code}] Starting TTS generation for text length: {len(text)}")

    try:
        output_filename = f"{code}.wav"
        output_filepath = os.path.join(export_path, output_filename)

        tts_model.generate_to_file(text, output_filepath, voice=voice, speed=0.9)

        file_urls = [f"/files/{code}/{output_filename}"]
        logger.info(f"[{code}] TTS succeeded")
        
        return {
            "output_path": export_path,
            "files": file_urls,
        }

    except Exception as e:
        logger.error(f"[{code}] TTS raised an exception: {e}")
        return {"error": str(e)}
    code = os.path.splitext(filename)[0]
    filepath = os.path.join(UPLOAD_DIR, filename)
    export_path = os.path.join(EXPORT_DIR, code)
    os.makedirs(export_path, exist_ok=True)

    logger.info(f"[{code}] Starting TTS processing for file: {filename}")

    try:
        # Read the text to synthesize from the uploaded file
        with open(filepath, 'r', encoding='utf-8') as f:
            text_to_speak = f.read().strip()
        
        if not text_to_speak:
            return {"error": "Uploaded text file is empty."}

        output_filename = f"{code}.wav"
        output_filepath = os.path.join(export_path, output_filename)

        logger.info(f"[{code}] Generating audio with voice: {voice}")
        tts_model.generate_to_file(text_to_speak, output_filepath, voice=voice, speed=0.9)

        # Exposed as URLs under the /files static mount
        file_urls = [f"/files/{code}/{output_filename}"]

        logger.info(f"[{code}] TTS succeeded, file produced: {output_filename}")
        return {
            "output_path": export_path,
            "files": file_urls,
        }

    except Exception as e:
        logger.error(f"[{code}] TTS raised an exception: {e}")
        return {"error": str(e)}

    finally:
        try:
            os.remove(filepath)
            logger.info(f"[{code}] Removed processed upload: {filepath}")
        except OSError as cleanup_err:
            logger.warning(f"[{code}] Failed to remove upload {filepath}: {cleanup_err}")