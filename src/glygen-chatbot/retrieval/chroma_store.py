from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from query.config import RAGConfig
from retrieval.chroma_client import ChromaSettings, load_vectorstore as _load_vectorstore


def load_vectorstore(config: RAGConfig, embeddings: HuggingFaceEmbeddings) -> Chroma:
    settings = ChromaSettings.from_env(
        collection_name=config.collection_name,
        chroma_dir=config.chroma_dir,
    )
    return _load_vectorstore(settings, embeddings)
