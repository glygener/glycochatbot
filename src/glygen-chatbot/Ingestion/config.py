import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_PDF_NAME = "Essential_of_Glycobiology_4E_EPUB_V5_InterVenn.pdf"
CONVERTED_TXT_NAME = "glycobiology.txt"
LEGACY_CONVERTED_TXT_NAME = "Essential_of_Glycobiology_4E_EPUB_V5_InterVenn (1)_extracted.txt"
FALLBACK_TXT_NAME = "fallback_glycobiology.txt"


def find_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    compose_markers = ("docker-compose.app.yml", "docker-compose.ingest.yml")
    for parent in [current, *current.parents]:
        if any((parent / marker).exists() for marker in compose_markers):
            return parent
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return current


def resolve_corpus_path(project_root: Path, data_dir: Path) -> Path:
    env_path = os.getenv("PDF_PATH") or os.getenv("CORPUS_PATH")
    if env_path:
        resolved = Path(env_path)
        if resolved.exists() and resolved.is_file():
            return resolved
        raise FileNotFoundError(f"Corpus file not found: {resolved}")

    pdf_path = project_root / DEFAULT_PDF_NAME
    if pdf_path.exists() and pdf_path.is_file():
        return pdf_path

    converted_dir = data_dir / "converted"
    for name in (CONVERTED_TXT_NAME, LEGACY_CONVERTED_TXT_NAME, FALLBACK_TXT_NAME):
        candidate = converted_dir / name
        if candidate.exists() and candidate.is_file():
            return candidate

    raise FileNotFoundError(
        "No textbook corpus found. Place the PDF at the project root "
        f"({DEFAULT_PDF_NAME}) or a converted .txt under data/converted/."
    )


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

        data_dir = Path(os.getenv("DATA_DIR", project_root / "data"))
        resolved_pdf = resolve_corpus_path(project_root, data_dir)

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
