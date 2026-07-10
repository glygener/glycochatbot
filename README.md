# GlyGen AI Chatbot

A **citation-first Retrieval-Augmented Generation (RAG) chatbot** for glycobiology students, built over *Essentials of Glycobiology, Fourth Edition*. Students ask questions in a **Streamlit chat UI**; the UI talks to a **FastAPI backend** over HTTP. Answers are grounded in the textbook with page-level citations — the system prefers refusal over hallucination when evidence is weak.

**Version:** 0.2.0 (Dockerized prototype)

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Get API Keys](#get-api-keys)
- [Prerequisites](#prerequisites)
- [Install From Scratch (Local)](#install-from-scratch-local)
- [Docker Installation and Run](#docker-installation-and-run)
- [How the Application Works](#how-the-application-works)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Configuration Reference](#configuration-reference)
- [Using the Streamlit UI](#using-the-streamlit-ui)
- [CLI (Optional)](#cli-optional)
- [How It Works Internally](#how-it-works-internally)
- [Data and Git](#data-and-git)
- [What's Implemented vs Planned](#whats-implemented-vs-planned)
- [Troubleshooting](#troubleshooting)

---

## Overview

GlyGen AI Chatbot answers glycobiology questions using only retrieved textbook passages (not general LLM knowledge).

| Layer | What runs |
|-------|-----------|
| **UI** | Streamlit → HTTP client (`GLYGEN_API_URL`) |
| **Backend** | FastAPI + `ChatOrchestrator` + RAG + SQLite |
| **Vectors** | ChromaDB (embedded locally, or HTTP server in Docker) |
| **LLM** | Groq `llama-3.1-8b-instant` |
| **Embeddings / rerank** | HuggingFace MiniLM + BGE reranker |

**Four Docker containers (optional):**

| ID | Service | Role |
|----|---------|------|
| C1 | `ingestion` | One-shot PDF indexing |
| C2 | `backend` | FastAPI + RAG + sessions |
| C3 | `chromadb` | Vector database server |
| C4 | `streamlit` | Chat UI |

---

## Quick Start

### Option A — Docker (recommended for full stack)

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and start it.
2. Get API keys ([below](#get-api-keys)).
3. Place the textbook PDF at the project root.
4. Create `.env` and run:

```bash
cp .env.example .env
# Edit .env with HF_TOKEN and GROQ_API_KEY

docker compose -f docker-compose.ingest.yml up --build
docker compose -f docker-compose.app.yml up --build
```

Open **http://localhost:8501**

### Option B — Local (no Docker)

```bash
pip install -r requirements.txt
cp .env.example .env   # add keys
# Place PDF at project root
cd src/glygen-chatbot
python -m Ingestion.pipeline
# Terminal 1:
uvicorn api.server:app --reload --host 127.0.0.1 --port 8000
# Terminal 2:
streamlit run api/streamlit_app.py
```

---

## Get API Keys

You need **two** keys. Create a free account on each site, then copy the token into `.env`.

### 1. HuggingFace token (`HF_TOKEN`)

Used to download embedding and reranker models.

| Step | Link / action |
|------|----------------|
| Sign up / log in | [https://huggingface.co/join](https://huggingface.co/join) |
| Create access token | [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| Token type | **Read** access is enough for model download |
| Put in `.env` | `HF_TOKEN=hf_...` |

### 2. Groq API key (`GROQ_API_KEY`)

Used for LLM answer generation (`llama-3.1-8b-instant`).

| Step | Link / action |
|------|----------------|
| Sign up / log in | [https://console.groq.com/](https://console.groq.com/) |
| Create API key | [https://console.groq.com/keys](https://console.groq.com/keys) |
| Put in `.env` | `GROQ_API_KEY=gsk_...` |

**Never commit `.env`.** It is listed in `.gitignore`.

---

## Prerequisites

### Local run

- **Python 3.11+**
- **Git**
- **HF_TOKEN** and **GROQ_API_KEY** (see above)
- Textbook PDF at project root:  
  `Essential_of_Glycobiology_4E_EPUB_V5_InterVenn.pdf`  
  (not in the GitHub repo — you must add it yourself)

### Docker run

- Everything above, plus:
- **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** installed and running
- Enough disk/RAM for model downloads (first build can take several minutes)

Verify Docker:

```bash
docker --version
docker compose version
```

---

## Install From Scratch (Local)

Follow these steps on a clean machine.

### Step 1 — Clone the repository

```bash
git clone <your-repo-url>
cd Glygen-AI-CHatbot
```

### Step 2 — Create a virtual environment

```bash
python -m venv .venv

# Windows (PowerShell / CMD)
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### Step 3 — Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Get API keys and create `.env`

1. Create tokens at:
   - HuggingFace: [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - Groq: [https://console.groq.com/keys](https://console.groq.com/keys)
2. Copy the example env file:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

3. Edit `.env`:

```env
HF_TOKEN=hf_your_token_here
GROQ_API_KEY=gsk_your_groq_key_here
GLYGEN_API_URL=http://127.0.0.1:8000
```

### Step 5 — Add the textbook PDF

Place this file in the **project root** (same folder as `README.md`):

```text
Glygen-AI-CHatbot/Essential_of_Glycobiology_4E_EPUB_V5_InterVenn.pdf
```

PDFs and `data/` are gitignored and are **not** pushed to GitHub.

### Step 6 — Ingest the textbook (one-time)

```bash
cd src/glygen-chatbot
python -m Ingestion.pipeline
```

This loads the PDF, chunks it (~1000 chars / 200 overlap), embeds with MiniLM, and stores vectors in `data/chroma/` (collection `glyco_corpus`). First run downloads HuggingFace models.

### Step 7 — Start the backend

From `src/glygen-chatbot`:

```bash
uvicorn api.server:app --reload --host 127.0.0.1 --port 8000
```

- API: http://127.0.0.1:8000  
- Docs: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/health  

### Step 8 — Start the Streamlit UI

Open a **second** terminal, activate `.venv`, then:

```bash
cd src/glygen-chatbot
streamlit run api/streamlit_app.py
```

Open **http://localhost:8501**

Streamlit calls the backend at `GLYGEN_API_URL` (default `http://127.0.0.1:8000`).

---

## Docker Installation and Run

Use this path if you want the full 4-container setup.

### What gets started

| Compose file | Containers | When to run |
|--------------|------------|-------------|
| `docker-compose.ingest.yml` | C3 ChromaDB + C1 Ingestion | Once (or when PDF changes) |
| `docker-compose.app.yml` | C3 ChromaDB + C2 Backend + C4 Streamlit | Every time you use the app |

Both share the named volume `glygen_chroma_data` so the app can read the index built by ingest.

### Step 1 — Install and start Docker Desktop

1. Download: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
2. Install and open Docker Desktop
3. Wait until it says Docker is running
4. Open a **new** terminal and confirm:

```bash
docker --version
docker compose version
```

### Step 2 — Clone, keys, PDF

```bash
git clone <your-repo-url>
cd Glygen-AI-CHatbot
copy .env.example .env   # or: cp .env.example .env
```

Edit `.env` with keys from:

- [HuggingFace tokens](https://huggingface.co/settings/tokens)
- [Groq API keys](https://console.groq.com/keys)

Place the PDF at project root:

```text
Essential_of_Glycobiology_4E_EPUB_V5_InterVenn.pdf
```

### Step 3 — Build and run ingestion (C1 + C3)

From the project root:

```bash
docker compose -f docker-compose.ingest.yml up --build
```

What this does:

- Starts ChromaDB on host port **8001**
- Mounts your PDF into the ingestion container
- Runs `python -m Ingestion.pipeline` once
- Writes embeddings into volume `glygen_chroma_data`
- Ingestion container exits when finished (`restart: "no"`)

First run may take a long time (image build + model download + ~1300 pages).

### Step 4 — Build and run the app (C2 + C3 + C4)

```bash
docker compose -f docker-compose.app.yml up --build
```

| URL | Service |
|-----|---------|
| http://localhost:8501 | Streamlit UI |
| http://localhost:8000 | FastAPI backend |
| http://localhost:8000/docs | Interactive API docs |
| http://localhost:8001 | ChromaDB (debug) |

Streamlit is configured with `GLYGEN_API_URL=http://backend:8000` inside Docker.

### Step 5 — Re-ingest after PDF updates

```bash
docker compose -f docker-compose.ingest.yml up ingestion --build
```

### Step 6 — Stop containers

```bash
docker compose -f docker-compose.app.yml down
docker compose -f docker-compose.ingest.yml down
```

Volumes (`glygen_chroma_data`, `chat_data`, `hf_cache`) persist so you do not lose the index or chat DB unless you remove volumes.

To wipe volumes as well:

```bash
docker compose -f docker-compose.app.yml down -v
```

### Docker file map

| File | Purpose |
|------|---------|
| `docker-compose.ingest.yml` | ChromaDB + ingestion job |
| `docker-compose.app.yml` | ChromaDB + backend + Streamlit |
| `docker/Dockerfile.app` | Image for backend and ingestion |
| `docker/Dockerfile.streamlit` | Lightweight Streamlit image |
| `.dockerignore` | Keeps builds smaller |

---

## How the Application Works

```
Student (Browser)
       │
       ▼
┌──────────────────────┐
│   Streamlit UI       │  streamlit_app.py
│   - Chat input       │
│   - Session sidebar  │
└──────────┬───────────┘
           │  HTTP (GLYGEN_API_URL)
           ▼
┌──────────────────────┐
│  FastAPI Backend     │  api/server.py
│  ChatOrchestrator    │
└──────────┬───────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
┌─────────┐  ┌──────────────┐
│RAG      │  │SessionStore  │
│Pipeline │  │(SQLite)      │
└────┬────┘  └──────────────┘
     │
     ▼
┌─────────┐
│ChromaDB │
│(vectors)│
└─────────┘
```

Each chat message: Streamlit → `POST /api/v1/chat` → classify → RAG or local handler → save to SQLite → return answer with page citation.

---

## Features

- Streamlit UI over HTTP to FastAPI
- PDF ingest → Chroma (`glyco_corpus`)
- Retrieve top-20 → BGE rerank top-5 → confidence gate
- Groq grounded JSON answers + page citations
- Session memory (name, recap, follow-ups) in SQLite
- Question routing: textbook / name / recap / out-of-scope
- Docker: 4 containers, 2 compose files
- Chroma HTTP mode (Docker) or embedded mode (local)
- CLI one-shot RAG via `main.py`

---

## Architecture

| Component | File | Role |
|-----------|------|------|
| Streamlit UI | `api/streamlit_app.py` | Chat + sidebar |
| HTTP client | `api/http_client.py` | Calls backend REST API |
| FastAPI | `api/server.py` | REST entry point |
| Orchestrator | `api/orchestrator.py` | Route + persist |
| RAG | `RAG/pipeline.py` | Retrieve → rerank → gate → generate |
| Chroma client | `retrieval/chroma_client.py` | HTTP or embedded |
| Sessions | `session/store.py` | SQLite |

### API endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Chroma + DB readiness |
| `GET` | `/api/v1/status` | Model / collection info |
| `POST` | `/api/v1/sessions` | Create session |
| `GET` | `/api/v1/sessions` | List sessions |
| `GET` | `/api/v1/sessions/{id}/messages` | History |
| `POST` | `/api/v1/chat` | Ask a question |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| UI | Streamlit |
| API | FastAPI + Uvicorn |
| LLM | Groq `llama-3.1-8b-instant` |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Reranker | `BAAI/bge-reranker-base` |
| Vector DB | ChromaDB |
| Sessions | SQLite |
| PDF | PyPDF / LangChain |
| Containers | Docker Compose |

---

## Project Structure

```
Glygen-AI-CHatbot/
├── main.py
├── plan.md
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore                 # ignores .env, *.pdf, data/
├── docker/
│   ├── Dockerfile.app
│   └── Dockerfile.streamlit
├── docker-compose.ingest.yml
├── docker-compose.app.yml
├── data/                      # local only (gitignored except .gitkeep)
│   └── .gitkeep
└── src/glygen-chatbot/
    ├── api/
    ├── RAG/
    ├── session/
    ├── retrieval/
    ├── generation/
    ├── query/
    └── Ingestion/
```

---

## Configuration Reference

| Variable | Required | Used by | Description |
|----------|----------|---------|-------------|
| `HF_TOKEN` | Yes | Ingest, Backend | HuggingFace — [create token](https://huggingface.co/settings/tokens) |
| `GROQ_API_KEY` | Yes | Backend | Groq — [create key](https://console.groq.com/keys) |
| `GLYGEN_API_URL` | Streamlit | UI | Backend URL (`http://127.0.0.1:8000` local; `http://backend:8000` in Docker) |
| `CHROMA_HOST` / `CHROMA_PORT` | Docker | Ingest, Backend | Set by compose; omit for local embedded Chroma |
| `PDF_PATH` | Docker ingest | Ingestion | PDF path inside container |
| `DATA_DIR` | Docker app | Backend | SQLite / data directory |

---

## Using the Streamlit UI

- **Chat input** — ask glycobiology questions
- **New chat** — new SQLite session
- **Sidebar** — switch between recent chats

| You say | Behavior |
|---------|----------|
| "My name is Alex" | Saves name (no LLM) |
| "What is glycosylation?" | Full RAG + page citation |
| "Tell me more about that" | Follow-up with prior context |
| "What did I ask?" | Session recap |
| "What's the weather?" | Out-of-scope refusal |

---

## CLI (Optional)

After local ingest (embedded Chroma):

```bash
# From project root, with venv active
python main.py "What is glycosylation?"
```

Prints JSON `RAGResponse`. No sessions / no Streamlit.

---

## How It Works Internally

### Ingestion

Load PDF → chunk (1000/200) → embed → store in `glyco_corpus`.

### RAG

Normalize → similarity k=20 → BGE top-5 → gate (min score -2.0) → Groq JSON → validate citations.

### Question types

`textbook_rag` | `session_name` | `session_recap` | `out_of_scope`

### Default models

| Setting | Value |
|---------|-------|
| Embedding | `all-MiniLM-L6-v2` |
| Reranker | `bge-reranker-base` |
| LLM | `llama-3.1-8b-instant` |
| Temperature | `0.0` |

---

## Data and Git

These are **not** committed to GitHub (see `.gitignore`):

- `.env` (secrets)
- `*.pdf` (textbook)
- `data/` contents (Chroma index, `chat.db`, converted text)

Only `data/.gitkeep` is kept so the folder exists after clone. You must add the PDF and run ingest yourself (local or Docker).

---

## What's Implemented vs Planned

### Done

- FastAPI + Streamlit (HTTP)
- RAG with gate and citations
- SQLite sessions
- Docker 4-container / 2-compose setup
- Chroma HTTP + embedded modes
- README / plan for current architecture

### Local vs Docker

| Mode | Chroma | Backend | UI |
|------|--------|---------|-----|
| Local | `data/chroma/` embedded | `uvicorn` | `streamlit` |
| Docker | Chroma container | `backend` | `streamlit` container |

### Still planned

- React UI + SSE streaming
- NCBI chapter/section metadata
- Evaluation question bank
- Rate limiting / CI/CD / cloud pilot

See [`plan.md`](plan.md) for the full architecture plan.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `docker` not recognized | Install/start [Docker Desktop](https://www.docker.com/products/docker-desktop/), open a new terminal |
| Missing `HF_TOKEN` / `GROQ_API_KEY` | Create keys at HuggingFace and Groq links above; put them in `.env` |
| PDF not found | Place `Essential_of_Glycobiology_4E_EPUB_V5_InterVenn.pdf` at project root |
| Streamlit can't reach backend | Local: start uvicorn first; set `GLYGEN_API_URL=http://127.0.0.1:8000` |
| Chroma empty in Docker app | Run `docker-compose.ingest.yml` before `docker-compose.app.yml` |
| First Docker build is slow | Normal — downloads base image + HF models into `hf_cache` |

---

## Acknowledgments

Built for glycomics education using *Essentials of Glycobiology*. Powered by Groq, HuggingFace, LangChain, ChromaDB, FastAPI, Streamlit, and Docker.
