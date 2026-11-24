import json

from langchain_core.documents import Document
from glyco_chroma.settings import find_project_root

BOOK_NAME = "Essentials of Glycobiology, Fourth Edition"
BOOK_URL = "https://www.ncbi.nlm.nih.gov/books/NBK579918/"
ONLINE_URL = "https://www.ncbi.nlm.nih.gov/books/n/glyco4/"
MAX_CHAPTER = 60


def _load_catalog() -> dict:
    root = find_project_root()
    path = root / "config" / "chapter_urls.json"
    if not path.exists():
        return {"book_name": BOOK_NAME, "book_url": BOOK_URL, "chapters": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def annotate_documents(documents: list[Document]) -> list[Document]:
    """Split corpus on chapter headings and attach NCBI chapter metadata."""
    catalog = _load_catalog()
    titles = _learn_titles(documents)
    # Prefer catalog titles when TOC parsing is thin
    for number, info in (catalog.get("chapters") or {}).items():
        try:
            n = int(number)
        except ValueError:
            continue
        titles.setdefault(n, info.get("name") or "")

    annotated: list[Document] = []
    current_number: int | None = None
    current_title: str | None = None

    for document in documents:
        for number, title, body in _segments(
            document.page_content, titles, current_number, current_title
        ):
            current_number = number
            current_title = title
            if not body.strip():
                continue
            metadata = dict(document.metadata)
            metadata["book_name"] = catalog.get("book_name") or BOOK_NAME
            if number is not None and title:
                chapter_info = (catalog.get("chapters") or {}).get(str(number), {})
                metadata["chapter_number"] = number
                metadata["chapter_name"] = chapter_info.get("name") or title
                metadata["chapter_url"] = (
                    chapter_info.get("url")
                    or catalog.get("online_edition")
                    or ONLINE_URL
                )
            else:
                metadata["chapter_url"] = catalog.get("book_url") or BOOK_URL
            # Prefer chapter citation over fake page labels from txt loader
            if metadata.get("page_label") == "extracted":
                metadata["page_label"] = (
                    f"Chapter {number}" if number is not None else "Front matter"
                )
            annotated.append(Document(page_content=body, metadata=metadata))

    return annotated or documents


def _learn_titles(documents: list[Document]) -> dict[int, str]:
    titles: dict[int, str] = {}
    for document in documents:
        lines = document.page_content.splitlines()
        for index, raw in enumerate(lines):
            number = _chapter_number(raw)
            if number is None:
                continue
            title = _next_text(lines, index + 1)
            if title is None or title.isupper() or len(title) > 140:
                continue
            titles.setdefault(number, title)
    return titles


def _segments(
    text: str,
    titles: dict[int, str],
    current_number: int | None,
    current_title: str | None,
):
    lines = text.splitlines()
    buffer: list[str] = []
    number = current_number
    title = current_title

    def flush():
        body = "\n".join(buffer).strip()
        buffer.clear()
        if body:
            return number, title, body
        return None

    index = 0
    while index < len(lines):
        chapter_number = _chapter_number(lines[index])
        if chapter_number is not None:
            heading = titles.get(chapter_number)
            nxt = _next_text(lines, index + 1)
            previous = _previous_text(lines, index - 1)
            if heading and nxt == heading and previous == BOOK_NAME:
                emitted = flush()
                if emitted is not None:
                    yield emitted
                number = chapter_number
                title = heading
        buffer.append(lines[index])
        index += 1

    emitted = flush()
    if emitted is not None:
        yield emitted


def _chapter_number(raw: str) -> int | None:
    text = raw.strip()
    if not text.isdigit():
        return None
    value = int(text)
    if 1 <= value <= MAX_CHAPTER:
        return value
    return None


def _next_text(lines: list[str], start: int) -> str | None:
    for line in lines[start:]:
        text = line.strip()
        if text:
            return text
    return None


def _previous_text(lines: list[str], start: int) -> str | None:
    for line in reversed(lines[: start + 1]):
        text = line.strip()
        if text:
            return text
    return None
