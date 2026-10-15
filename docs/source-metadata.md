# Source metadata

Ingestion reads `data/converted/glycobiology.txt` (or a PDF) and splits it on chapter headings before chunking. A heading is the book-title line, then a line that is only the chapter number, then the title from the table of contents. Contents entries are not treated as chapters.

Each chunk stored in Chroma has:

| Field | Value |
|-------|--------|
| `book_name` | Essentials of Glycobiology, Fourth Edition |
| `chapter_number` | Integer, when the chunk is inside a chapter |
| `chapter_name` | Title from the contents, when known |
| `chapter_url` | `https://www.ncbi.nlm.nih.gov/books/n/glyco4` when the chapter is known |

Front matter before chapter 1 keeps the book name and omits the chapter fields. Retrieval copies these fields into the prompt context. The model must copy them into the citation and must not invent a chapter or link. The chat footer shows the book, chapter number, chapter name, and link when they are present. If they are missing, the footer stays `Essentials of Glycobiology`, Page ….

Re-run ingestion after changing this metadata. Ingestion replaces the `glyco_corpus` collection so older chunks are not left in the index.
