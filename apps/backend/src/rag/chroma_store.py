from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from glyco_chroma.settings import ChromaSettings
from glyco_chroma.store import load_vectorstore as _load_vectorstore

from rag.config import RAGConfig


def load_vectorstore(config: RAGConfig, embeddings: HuggingFaceEmbeddings) -> Chroma:
    settings = ChromaSettings.from_env(
        collection_name=config.collection_name,
        chroma_dir=config.chroma_dir,
    )
    return _load_vectorstore(settings, embeddings)
