import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def find_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return current


@dataclass(frozen=True)
class IngestionConfig:
    project_root: Path
    pdf_path: Path
    chroma_dir: Path
    collection_name: str = "glyco_corpus"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200

    @classmethod
    def from_env(cls, start: Path | None = None) -> "IngestionConfig":
        project_root = find_project_root(start)
        load_dotenv(project_root / ".env")

        pdf_path = os.getenv("PDF_PATH")
        if pdf_path:
            resolved_pdf = Path(pdf_path)
        else:
            resolved_pdf = (
                project_root / "Essential_of_Glycobiology_4E_EPUB_V5_InterVenn.pdf"
            )

        data_dir = Path(os.getenv("DATA_DIR", project_root / "data"))

        return cls(
            project_root=project_root,
            pdf_path=resolved_pdf,
            chroma_dir=data_dir / "chroma",
        )

    @property
    def hf_token(self) -> str:
        token = os.getenv("HF_TOKEN")
        if not token:
            raise ValueError("HF_TOKEN is not set. Add it to .env in the project root.")
        return token
