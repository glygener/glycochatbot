from generation.schemas import SourceCitation


def format_display_answer(answer: str, sources: list[SourceCitation] | list[dict]) -> str:
    if not sources:
        return answer

    source = sources[0]
    if hasattr(source, "page_label"):
        page_label = source.page_label
        page = source.page
    else:
        page_label = source.get("page_label")
        page = source.get("page")

    page = page_label or page or "?"
    return (
        f"{answer.strip()}\n\n---\n"
        f"**Source:** *Essentials of Glycobiology*, Page {page}"
    )


def best_source(sources: list[SourceCitation]) -> list[SourceCitation]:
    if not sources:
        return []
    return [sources[0]]
