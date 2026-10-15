from langchain_core.documents import Document

BOOK_NAME = "Essentials of Glycobiology, Fourth Edition"
BOOK_URL = "https://www.ncbi.nlm.nih.gov/books/n/glyco4"
MAX_CHAPTER = 60


def annotate_documents(documents: list[Document]) -> list[Document]:
    """Split corpus text on chapter headings and attach source metadata.

    Chapter headings in this textbook are a number on its own line followed by
    the chapter title. Front matter before the first chapter keeps the book
    name and leaves chapter fields empty.
    """
    titles = _learn_titles(documents)
    annotated: list[Document] = []
    current_number: int | None = None
    current_title: str | None = None

    for document in documents:
        for number, title, body in _segments(document.page_content, titles, current_number, current_title):
            current_number = number
            current_title = title
            if not body.strip():
                continue
            metadata = dict(document.metadata)
            metadata["book_name"] = BOOK_NAME
            if number is not None and title:
                metadata["chapter_number"] = number
                metadata["chapter_name"] = title
                metadata["chapter_url"] = BOOK_URL
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
    number = int(text)
    if 1 <= number <= MAX_CHAPTER:
        return number
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
