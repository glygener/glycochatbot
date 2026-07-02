import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from Ingestion.config import find_project_root


@dataclass(frozen=True)
class RAGConfig:
    project_root: Path
    chroma_dir: Path
    collection_name: str = "glyco_corpus"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    reranker_model: str = "BAAI/bge-reranker-base"
    llm_model: str = "llama-3.1-8b-instant"
    top_k_retrieval: int = 20
    top_k_rerank: int = 5
    min_rerank_score: float = -2.0
    temperature: float = 0.0

    @classmethod
    def from_env(cls, start: Path | None = None) -> "RAGConfig":
        project_root = find_project_root(start)
        load_dotenv(project_root / ".env")

        return cls(
            project_root=project_root,
            chroma_dir=project_root / "data" / "chroma",
        )

    @property
    def hf_token(self) -> str:
        token = os.getenv("HF_TOKEN")
        if not token:
            raise ValueError("HF_TOKEN is not set. Add it to .env in the project root.")
        return token

    @property
    def groq_api_key(self) -> str:
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError("GROQ_API_KEY is not set. Add it to .env in the project root.")
        return key
