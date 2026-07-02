from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_core.documents import Document

from query.config import RAGConfig


class BGEReranker:
    def __init__(self, config: RAGConfig) -> None:
        self.config = config
        self._encoder = HuggingFaceCrossEncoder(
            model_name=config.reranker_model,
            model_kwargs={"token": config.hf_token},
        )

    def rerank(self, query: str, documents: list[Document]) -> list[tuple[Document, float]]:
        if not documents:
            return []

        pairs = [(query, doc.page_content) for doc in documents]
        scores = self._encoder.score(pairs)
        ranked = sorted(zip(documents, scores), key=lambda item: item[1], reverse=True)
        return ranked[: self.config.top_k_rerank]
