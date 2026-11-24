# Source metadata (chapter citations)

Answers cite **chapters** from *Essentials of Glycobiology, Fourth Edition* (NCBI Bookshelf), not PDF page numbers.

## Fields on each chunk

| Field | Meaning |
|-------|---------|
| `book_name` | Essentials of Glycobiology, Fourth Edition |
| `chapter_number` | 1–60 when known |
| `chapter_name` | Title from TOC / `config/chapter_urls.json` |
| `chapter_url` | NCBI chapter or edition link |

Book hub: https://www.ncbi.nlm.nih.gov/books/NBK579918/

Catalog: `config/chapter_urls.json`. Ingestion (`ingestion/chapters.py`) splits on chapter headings and attaches these fields before chunking. Re-run ingestion after changing the catalog.

## Footer example

```text
Source: Essentials of Glycobiology, Fourth Edition, Chapter 1: Historical Background and Overview
https://www.ncbi.nlm.nih.gov/books/NBK579927/
```
