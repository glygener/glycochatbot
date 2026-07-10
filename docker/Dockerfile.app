FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml .
COPY src/glygen-chatbot ./src/glygen-chatbot

WORKDIR /app/src/glygen-chatbot
ENV PYTHONPATH=/app/src/glygen-chatbot
ENV PYTHONUNBUFFERED=1
