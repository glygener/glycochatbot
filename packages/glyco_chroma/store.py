import time
from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from .settings import ChromaSettings


def _http_client(settings: ChromaSettings, retries: int = 30, delay: float = 2.0) -> chromadb.HttpClient:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            client = chromadb.HttpClient(host=settings.host, port=settings.port)
            client.heartbeat()
            return client
        except Exception as exc:
            last_error = exc
            if attempt < retries - 1:
                time.sleep(delay)
    raise ConnectionError(
        f"Could not connect to ChromaDB at {settings.host}:{settings.port}"
    ) from last_error


def chroma_is_ready(settings: ChromaSettings) -> bool:
    if settings.use_http:
        try:
            _http_client(settings, retries=1, delay=0)
            return True
        except Exception:
            return False
    return settings.chroma_dir is not None and settings.chroma_dir.exists()


def load_vectorstore(
    settings: ChromaSettings,
    embeddings: HuggingFaceEmbeddings,
) -> Chroma:
    if settings.use_http:
        client = _http_client(settings)
        return Chroma(
            client=client,
            collection_name=settings.collection_name,
            embedding_function=embeddings,
        )

    if settings.chroma_dir is None or not settings.chroma_dir.exists():
        raise FileNotFoundError(
            f"Chroma directory not found: {settings.chroma_dir}. Run ingestion first."
        )

    return Chroma(
        collection_name=settings.collection_name,
        embedding_function=embeddings,
        persist_directory=str(settings.chroma_dir),
    )


def store_documents(
    settings: ChromaSettings,
    embeddings: HuggingFaceEmbeddings,
    chunks: list[Document],
) -> Chroma:
    if settings.use_http:
        client = _http_client(settings)
        return Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=settings.collection_name,
            client=client,
        )

    if settings.chroma_dir is None:
        raise ValueError("chroma_dir is required when not using HTTP Chroma.")

    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=settings.collection_name,
        persist_directory=str(settings.chroma_dir),
    )
