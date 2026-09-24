from langchain_huggingface import HuggingFaceEmbeddings

from .config import IngestionConfig


def create_embeddings(config: IngestionConfig) -> HuggingFaceEmbeddings:
    # Always the free MiniLM embedder from config/llms.json ingest settings.
    # LLM_OPTION only selects the chat model for response generation.
    return HuggingFaceEmbeddings(
        model_name=config.embedding_model,
        model_kwargs={"token": config.hf_token},
        encode_kwargs={"normalize_embeddings": True},
    )
