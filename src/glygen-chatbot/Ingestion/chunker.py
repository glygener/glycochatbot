from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import IngestionConfig


def chunk_documents(
    documents: list[Document],
    config: IngestionConfig,
) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)
