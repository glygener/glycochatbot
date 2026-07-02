from langchain_core.documents import Document


def build_context(docs: list[Document]) -> str:
    blocks: list[str] = []
    for index, doc in enumerate(docs, start=1):
        page = doc.metadata.get("page")
        page_label = doc.metadata.get("page_label", "?")
        blocks.append(
            f"[SOURCE {index} | page_index={page} | page_label={page_label}]\n"
            f"{doc.page_content.strip()}"
        )
    return "\n\n".join(blocks)
