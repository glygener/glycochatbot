from langchain_chroma import Chroma
from langchain_core.documents import Document

from rag.config import RAGConfig


class VectorRetriever:
    def __init__(self, vectorstore: Chroma, config: RAGConfig) -> None:
        self.vectorstore = vectorstore
        self.config = config

    def retrieve(self, query: str) -> list[Document]:
        return self.vectorstore.similarity_search(query, k=self.config.top_k_retrieval)
