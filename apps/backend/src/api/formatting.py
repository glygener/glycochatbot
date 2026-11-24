from rag.schemas import SourceCitation


def _source_value(source: SourceCitation | dict, name: str):
    if isinstance(source, dict):
        return source.get(name)
    return getattr(source, name, None)


def format_display_answer(answer: str, sources: list[SourceCitation] | list[dict]) -> str:
    if not sources:
        return answer

    source = sources[0]
    book_name = _source_value(source, "book_name")
    chapter_number = _source_value(source, "chapter_number")
    chapter_name = _source_value(source, "chapter_name")
    chapter_url = _source_value(source, "chapter_url")
    page_label = _source_value(source, "page_label")
    page = _source_value(source, "page")

    if book_name or chapter_name or chapter_number:
        book = book_name or "Essentials of Glycobiology, Fourth Edition"
        parts = [f"**Source:** *{book}*"]
        if chapter_number and chapter_name:
            parts.append(f"Chapter {chapter_number}: {chapter_name}")
        elif chapter_name:
            parts.append(str(chapter_name))
        elif chapter_number:
            parts.append(f"Chapter {chapter_number}")
        attribution = ", ".join(parts)
        if chapter_url:
            attribution = f"{attribution}\n{chapter_url}"
    else:
        page_text = page_label or page
        if page_text and str(page_text) not in {"extracted", "0", "?", "None"}:
            attribution = f"**Source:** *Essentials of Glycobiology*, {page_text}"
        else:
            attribution = (
                "**Source:** *Essentials of Glycobiology, Fourth Edition*\n"
                "https://www.ncbi.nlm.nih.gov/books/NBK579918/"
            )

    return f"{answer.strip()}\n\n---\n{attribution}"


def best_source(sources: list[SourceCitation]) -> list[SourceCitation]:
    if not sources:
        return []
    return [sources[0]]
