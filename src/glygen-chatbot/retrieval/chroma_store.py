from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from query.config import RAGConfig


def load_vectorstore(config: RAGConfig, embeddings: HuggingFaceEmbeddings) -> Chroma:
    if not config.chroma_dir.exists():
        raise FileNotFoundError(
            f"Chroma directory not found: {config.chroma_dir}. Run ingestion first."
        )

    return Chroma(
        collection_name=config.collection_name,
        embedding_function=embeddings,
        persist_directory=str(config.chroma_dir),
    )
