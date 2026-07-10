from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from retrieval.chroma_client import ChromaSettings, load_vectorstore, store_documents

from .chunker import chunk_documents
from .config import IngestionConfig
from .embedder import create_embeddings
from .loader import load_pdf


class IngestionPipeline:
    def __init__(self, config: IngestionConfig | None = None) -> None:
        self.config = config or IngestionConfig.from_env()
        self.embeddings: HuggingFaceEmbeddings | None = None
        self.vectorstore: Chroma | None = None

    def _chroma_settings(self) -> ChromaSettings:
        return ChromaSettings.from_env(
            collection_name=self.config.collection_name,
            chroma_dir=self.config.chroma_dir,
        )

    def load(self) -> list[Document]:
        return load_pdf(self.config.pdf_path)

    def chunk(self, documents: list[Document]) -> list[Document]:
        return chunk_documents(documents, self.config)

    def get_embeddings(self) -> HuggingFaceEmbeddings:
        if self.embeddings is None:
            self.embeddings = create_embeddings(self.config)
        return self.embeddings

    def store(self, chunks: list[Document]) -> Chroma:
        embeddings = self.get_embeddings()
        self.vectorstore = store_documents(self._chroma_settings(), embeddings, chunks)
        return self.vectorstore

    def load_vectorstore(self) -> Chroma:
        self.vectorstore = load_vectorstore(self._chroma_settings(), self.get_embeddings())
        return self.vectorstore

    def run(self) -> Chroma:
        documents = self.load()
        chunks = self.chunk(documents)
        return self.store(chunks)

    def similarity_search(self, query: str, k: int = 3) -> list[Document]:
        vectorstore = self.vectorstore or self.load_vectorstore()
        return vectorstore.similarity_search(query, k=k)


if __name__ == "__main__":
    pipeline = IngestionPipeline()
    vectorstore = pipeline.run()

    query = "What are glycans?"
    results = pipeline.similarity_search(query, k=3)

    settings = pipeline._chroma_settings()
    print(f"Stored in collection: {pipeline.config.collection_name}")
    if settings.use_http:
        print(f"Chroma server: {settings.host}:{settings.port}")
    else:
        print(f"Persist directory: {pipeline.config.chroma_dir}")
    print(f"\nQuery: {query}\n")

    for i, doc in enumerate(results, start=1):
        print(f"--- Result {i} ---")
        print(doc.page_content[:400])
        print(doc.metadata)
        print()
