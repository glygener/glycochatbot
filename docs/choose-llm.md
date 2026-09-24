# Choose LLM / LLM API from configuration

Runtime selection of the **chat** model used for response generation. Embeddings and ranking are not switched with this setting.

## How to switch

In `.env` at the project root:

```env
LLM_OPTION=free
```

| Value | Model | Key required |
|-------|--------|----------------|
| `free` (default if unset or empty) | Groq `openai/gpt-oss-20b` | `GROQ_API_KEY` |
| `openai` | OpenAI `gpt-4o-mini` | `OPENAI_API_KEY` |

Restart the backend after changing `LLM_OPTION`. Ingestion does not need a restart for this value.

Confirm the active model:

```text
GET http://127.0.0.1:8000/api/v1/status
```

The response includes `llm_option`, `llm_provider`, and `llm_model`.

## Configuration file

[`config/llms.json`](../config/llms.json) is the catalog. `LLM_OPTION` must match a key under `options`.

Each option stores:

- `provider` / `model` / `temperature`
- `prompt_dir`
- `chunk_size` / `chunk_overlap` (documented per LLM; ingest uses the `ingest` block instead)
- `top_k_retrieval` / `top_k_rerank` / `min_rerank_score`
- `ranking_strategy` (`bge` — not used to pick an LLM ranker)

The `ingest` block is always used for embedding generation (MiniLM). The `reranker` block records BGE; the chat LLM is not used for ranking.

Optional override: `LLM_CONFIG_PATH` pointing at another JSON file.

To use a different Groq model, change `options.free.model` in `llms.json`.

## Prompts folder

Prompts are files, not hardcoded in the generator:

```text
prompts/
  free/
    system.txt
    human.txt
  openai/
    system.txt
    human.txt
```

`{context}` and `{question}` in `human.txt` are filled at runtime. JSON examples in `system.txt` use doubled braces (`{{` / `}}`) so LangChain does not treat them as variables.

## Source changes

| Area | Change |
|------|--------|
| `packages/llm/` | Load JSON, load prompt files, build Groq or OpenAI chat client |
| `apps/backend/src/rag/generator.py` | Uses `create_chat_llm()` and prompt files instead of hardcoded `ChatGroq` |
| `apps/backend/src/rag/config.py` | Reads `LLM_OPTION` + `config/llms.json` |
| `apps/ingestion/` | Chunk/embed settings from the JSON `ingest` block; **ignores** `LLM_OPTION` |
| `apps/backend/src/rag/pipeline.py` | Retrieval embeddings stay MiniLM |
| `apps/backend/src/rag/reranker.py` | Still BGE only |
| `.env.example` | Documents `LLM_OPTION`, `OPENAI_API_KEY` |
| Docker backend/ingest images | Copy `config/` (and `prompts/` for backend) |

## What stays the same

- Ingest and query embeddings: `sentence-transformers/all-MiniLM-L6-v2`
- Reranking: `BAAI/bge-reranker-base`
- UI, sessions, Chroma collection, citation JSON schema
