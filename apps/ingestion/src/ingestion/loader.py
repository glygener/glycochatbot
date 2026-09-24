from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


def load_documents(source_path: Path) -> list[Document]:
    if not source_path.exists() or not source_path.is_file():
        raise FileNotFoundError(f"Corpus file not found: {source_path}")

    suffix = source_path.suffix.lower()
    if suffix == ".pdf":
        return PyPDFLoader(str(source_path)).load()
    if suffix == ".txt":
        text = source_path.read_text(encoding="utf-8", errors="replace")
        return [
            Document(
                page_content=text,
                metadata={
                    "source": str(source_path),
                    "page": 0,
                    "page_label": "extracted",
                },
            )
        ]

    raise ValueError(f"Unsupported corpus file type: {source_path}")
