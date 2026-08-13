FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml .
COPY src/glygen-chatbot ./src/glygen-chatbot
COPY data/converted ./data/converted

WORKDIR /app/src/glygen-chatbot
ENV PYTHONPATH=/app/src/glygen-chatbot
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/root/.cache/huggingface
