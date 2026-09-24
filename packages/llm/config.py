from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_LLM_OPTION = "free"
DEFAULT_CONFIG_RELATIVE = Path("config") / "llms.json"


@dataclass(frozen=True)
class LLMOption:
    key: str
    display_name: str
    provider: str
    model: str
    temperature: float
    chunk_size: int
    chunk_overlap: int
    top_k_retrieval: int
    top_k_rerank: int
    min_rerank_score: float
    ranking_strategy: str
    prompt_dir: str


@dataclass(frozen=True)
class IngestSettings:
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    reranker_model: str


def llm_config_path(project_root: Path) -> Path:
    override = os.getenv("LLM_CONFIG_PATH")
    if override:
        return Path(override)
    return project_root / DEFAULT_CONFIG_RELATIVE


def load_llm_catalog(project_root: Path) -> dict:
    path = llm_config_path(project_root)
    if not path.exists():
        raise FileNotFoundError(
            f"LLM config not found: {path}. Expected config/llms.json at the project root."
        )
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def available_llm_keys(catalog: dict) -> list[str]:
    options = catalog.get("options") or {}
    return sorted(options.keys())


def resolve_llm_option(project_root: Path) -> LLMOption:
    catalog = load_llm_catalog(project_root)
    default = str(catalog.get("default") or DEFAULT_LLM_OPTION).strip().lower()
    raw = os.getenv("LLM_OPTION")
    key = (raw or default or DEFAULT_LLM_OPTION).strip().lower()
    if not key:
        key = DEFAULT_LLM_OPTION

    options = catalog.get("options") or {}
    if key not in options:
        known = ", ".join(available_llm_keys(catalog)) or "(none)"
        raise ValueError(f"Unknown LLM_OPTION={key!r}. Valid keys: {known}")

    data = options[key]
    return LLMOption(
        key=key,
        display_name=str(data.get("display_name") or key),
        provider=str(data["provider"]).strip().lower(),
        model=str(data["model"]),
        temperature=float(data.get("temperature", 0.0)),
        chunk_size=int(data.get("chunk_size", 1000)),
        chunk_overlap=int(data.get("chunk_overlap", 200)),
        top_k_retrieval=int(data.get("top_k_retrieval", 20)),
        top_k_rerank=int(data.get("top_k_rerank", 5)),
        min_rerank_score=float(data.get("min_rerank_score", -2.0)),
        ranking_strategy=str(data.get("ranking_strategy") or "bge"),
        prompt_dir=str(data.get("prompt_dir") or f"prompts/{key}"),
    )


def load_ingest_settings(project_root: Path) -> IngestSettings:
    """Embedding/chunk settings. Always the free MiniLM path; ignores LLM_OPTION."""
    catalog = load_llm_catalog(project_root)
    ingest = catalog.get("ingest") or {}
    reranker = catalog.get("reranker") or {}
    return IngestSettings(
        embedding_model=str(
            ingest.get("embedding_model") or "sentence-transformers/all-MiniLM-L6-v2"
        ),
        chunk_size=int(ingest.get("chunk_size", 1000)),
        chunk_overlap=int(ingest.get("chunk_overlap", 200)),
        reranker_model=str(reranker.get("model") or "BAAI/bge-reranker-base"),
    )
