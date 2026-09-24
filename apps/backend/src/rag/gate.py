from langchain_core.documents import Document

from rag.config import RAGConfig


class RetrievalGate:
    """Block generation when retrieved context is too weak."""

    def __init__(self, config: RAGConfig) -> None:
        self.config = config

    def passes(self, ranked: list[tuple[Document, float]]) -> bool:
        if not ranked:
            return False
        return ranked[0][1] >= self.config.min_rerank_score
