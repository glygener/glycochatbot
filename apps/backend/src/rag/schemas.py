from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    source_id: int
    page: int | None = None
    page_label: str | None = None
    book_name: str | None = None
    chapter_number: int | str | None = None
    chapter_name: str | None = None
    chapter_url: str | None = None
    excerpt: str
    relevance: str


class RAGResponse(BaseModel):
    answer: str
    confidence: str = Field(description="high | medium | low | insufficient")
    in_scope: bool
    sources: list[SourceCitation]
    refusal_reason: str | None = None
