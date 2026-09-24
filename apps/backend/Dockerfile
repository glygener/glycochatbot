FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY apps/backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY packages /app/packages
COPY apps/backend /app/apps/backend
COPY config /app/config
COPY prompts /app/prompts

WORKDIR /app/apps/backend/src
ENV PYTHONPATH=/app/packages:/app/apps/backend/src
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/root/.cache/huggingface
