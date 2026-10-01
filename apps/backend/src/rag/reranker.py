from langchain_core.documents import Document

from rag.config import RAGConfig


class BGEReranker:
    """Keep retrieval order. The BGE cross-encoder is not loaded.

    Loading BAAI/bge-reranker-base exhausted Windows memory and froze the API,
    which made Streamlit time out on ordinary session calls.
    """

    def __init__(self, config: RAGConfig) -> None:
        self.config = config

    def rerank(self, query: str, documents: list[Document]) -> list[tuple[Document, float]]:
        del query
        if not documents:
            return []
        # Score 0 stays above the retrieval gate (min_rerank_score is negative).
        return [(doc, 0.0) for doc in documents[: self.config.top_k_rerank]]
