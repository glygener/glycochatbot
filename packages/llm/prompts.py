from pathlib import Path


def load_chat_prompts(project_root: Path, prompt_dir: str) -> tuple[str, str]:
    directory = Path(prompt_dir)
    if not directory.is_absolute():
        directory = project_root / directory

    system_path = directory / "system.txt"
    human_path = directory / "human.txt"
    missing = [str(path) for path in (system_path, human_path) if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "LLM prompt files not found: " + ", ".join(missing)
        )
    return (
        system_path.read_text(encoding="utf-8").strip(),
        human_path.read_text(encoding="utf-8").strip(),
    )
