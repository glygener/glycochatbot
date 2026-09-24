import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from glyco_chroma.settings import find_project_root
from llm.config import LLMOption, load_ingest_settings, resolve_llm_option


@dataclass(frozen=True)
class RAGConfig:
    project_root: Path
    chroma_dir: Path
    llm: LLMOption
    collection_name: str = "glyco_corpus"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    reranker_model: str = "BAAI/bge-reranker-base"
    ranking_strategy: str = "bge"

    @classmethod
    def from_env(cls, start: Path | None = None) -> "RAGConfig":
        project_root = find_project_root(start)
        load_dotenv(project_root / ".env")

        data_dir = Path(os.getenv("DATA_DIR", project_root / "data"))
        llm = resolve_llm_option(project_root)
        ingest = load_ingest_settings(project_root)

        return cls(
            project_root=project_root,
            chroma_dir=data_dir / "chroma",
            llm=llm,
            embedding_model=ingest.embedding_model,
            reranker_model=ingest.reranker_model,
            ranking_strategy=llm.ranking_strategy or "bge",
        )

    @property
    def llm_option(self) -> str:
        return self.llm.key

    @property
    def llm_provider(self) -> str:
        return self.llm.provider

    @property
    def llm_model(self) -> str:
        return self.llm.model

    @property
    def prompt_dir(self) -> str:
        return self.llm.prompt_dir

    @property
    def temperature(self) -> float:
        return self.llm.temperature

    @property
    def top_k_retrieval(self) -> int:
        return self.llm.top_k_retrieval

    @property
    def top_k_rerank(self) -> int:
        return self.llm.top_k_rerank

    @property
    def min_rerank_score(self) -> float:
        return self.llm.min_rerank_score

    @property
    def hf_token(self) -> str:
        token = os.getenv("HF_TOKEN")
        if not token:
            raise ValueError("HF_TOKEN is not set. Add it to .env in the project root.")
        return token
