from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from .chunker import chunk_documents
from .config import IngestionConfig
from .embedder import create_embeddings
from .loader import load_pdf


class IngestionPipeline:
    def __init__(self, config: IngestionConfig | None = None) -> None:
        self.config = config or IngestionConfig.from_env()
        self.embeddings: HuggingFaceEmbeddings | None = None
        self.vectorstore: Chroma | None = None

    def load(self) -> list[Document]:
        return load_pdf(self.config.pdf_path)

    def chunk(self, documents: list[Document]) -> list[Document]:
        return chunk_documents(documents, self.config)

    def get_embeddings(self) -> HuggingFaceEmbeddings:
        if self.embeddings is None:
            self.embeddings = create_embeddings(self.config)
        return self.embeddings

    def store(self, chunks: list[Document]) -> Chroma:
        self.config.chroma_dir.mkdir(parents=True, exist_ok=True)
        embeddings = self.get_embeddings()

        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=self.config.collection_name,
            persist_directory=str(self.config.chroma_dir),
        )
        return self.vectorstore

    def load_vectorstore(self) -> Chroma:
        self.vectorstore = Chroma(
            collection_name=self.config.collection_name,
            embedding_function=self.get_embeddings(),
            persist_directory=str(self.config.chroma_dir),
        )
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

    print(f"Stored in collection: {pipeline.config.collection_name}")
    print(f"Persist directory: {pipeline.config.chroma_dir}")
    print(f"\nQuery: {query}\n")

    for i, doc in enumerate(results, start=1):
        print(f"--- Result {i} ---")
        print(doc.page_content[:400])
        print(doc.metadata)
        print()
