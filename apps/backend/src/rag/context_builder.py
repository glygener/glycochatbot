from langchain_core.documents import Document


def build_context(docs: list[Document]) -> str:
    blocks: list[str] = []
    for index, doc in enumerate(docs, start=1):
        page = doc.metadata.get("page")
        page_label = doc.metadata.get("page_label", "?")
        book_name = doc.metadata.get("book_name") or ""
        chapter_number = doc.metadata.get("chapter_number") or ""
        chapter_name = doc.metadata.get("chapter_name") or ""
        chapter_url = doc.metadata.get("chapter_url") or ""
        blocks.append(
            "[SOURCE {index} | page_index={page} | page_label={page_label}"
            " | book_name={book_name} | chapter_number={chapter_number}"
            " | chapter_name={chapter_name} | chapter_url={chapter_url}]\n"
            "{content}".format(
                index=index,
                page=page,
                page_label=page_label,
                book_name=book_name,
                chapter_number=chapter_number,
                chapter_name=chapter_name,
                chapter_url=chapter_url,
                content=doc.page_content.strip(),
            )
        )
    return "\n\n".join(blocks)
