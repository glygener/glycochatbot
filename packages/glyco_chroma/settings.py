import os
from dataclasses import dataclass
from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    markers = (
        "docker-compose.app.yml",
        "docker-compose.ingest.yml",
        ".env.example",
        "config/llms.json",
    )
    for parent in [current, *current.parents]:
        if any((parent / marker).exists() for marker in markers):
            return parent
        if (parent / "infra" / "docker-compose.app.yml").exists():
            return parent
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return current


@dataclass(frozen=True)
class ChromaSettings:
    collection_name: str
    chroma_dir: Path | None = None
    host: str | None = None
    port: int = 8000

    @classmethod
    def from_env(
        cls,
        collection_name: str = "glyco_corpus",
        chroma_dir: Path | None = None,
    ) -> "ChromaSettings":
        host = os.getenv("CHROMA_HOST") or None
        port = int(os.getenv("CHROMA_PORT", "8000"))
        return cls(
            collection_name=collection_name,
            chroma_dir=chroma_dir,
            host=host,
            port=port,
        )

    @property
    def use_http(self) -> bool:
        return self.host is not None
