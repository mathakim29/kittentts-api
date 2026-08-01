FROM pytorch/pytorch:2.13.0-cuda13.0-cudnn9-runtime

WORKDIR /app

RUN pip install --break-system-packages \
    fastapi uvicorn python-multipart \
    redis rq \
    https://github.com/KittenML/KittenTTS/releases/download/0.8.1/kittentts-0.8.1-py3-none-any.whl \
    python-dotenv onnxruntime[gpu]

RUN apt-get update && apt-get install -y redis ffmpeg \
    && rm -rf /var/lib/apt/lists/*