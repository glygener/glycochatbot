# Multi-sentence responses

Choices for richer textbook answers. Chunk size and ranking were not changed for this work. Embeddings stay `sentence-transformers/all-MiniLM-L6-v2`.

## Model and API

Paid chat uses OpenAI `gpt-4o` when `LLM_OPTION=openai`. That value is `options.openai` in `config/llms.json`. Temperature is `0.0`.

The client is `langchain_openai.ChatOpenAI` in `packages/llm/openai.py`. LangChain sends the prompt to the OpenAI Chat Completions API (`/v1/chat/completions`). The key is `OPENAI_API_KEY`.

`apps/backend/src/rag/generator.py` builds that client with `create_chat_llm(config.llm)` and loads `prompts/openai/system.txt` and `prompts/openai/human.txt`. The free option uses the same prompt shape from `prompts/free/` with Groq `openai/gpt-oss-20b`.

Switch models by setting `LLM_OPTION` and restarting the backend. Confirm with `GET /api/v1/status` (`llm_option`, `llm_provider`, `llm_model`). See [choose-llm.md](choose-llm.md).

## Prompting strategies

`prompts/openai/system.txt` and `prompts/free/system.txt` use the same three strategies.

1. **Rules with no example first (zero-shot).** Lines 4–13: answer only from CONTEXT, refuse when the text is irrelevant, and do not invent pages or examples.
2. **Interview outline.** Lines 6–11: paragraph 1 says what the subject is, paragraph 2 says how it works or why it matters, paragraph 3 gives one example only when CONTEXT contains one. Skip a paragraph the text cannot support. Write 2–4 short paragraphs.
3. **Few-shot examples.** Lines 43–70: a grounded multi-paragraph JSON answer. Lines 72–87: a refusal when CONTEXT does not answer the question, with `sources` empty and `in_scope` false.

`prompts/openai/human.txt` lines 7–8 tell the model to follow that outline and return one JSON object.

## Guard rails

| Rule | Where |
|------|--------|
| Use only CONTEXT. Do not add outside knowledge or examples. | `prompts/openai/system.txt` lines 4 and 8–13 |
| 2–4 paragraphs. Skip a paragraph CONTEXT cannot support. Set confidence to `low` when the text is thin. | `prompts/openai/system.txt` lines 6–12 |
| If nothing relevant, set `in_scope` false and explain in `refusal_reason`. | `prompts/openai/system.txt` line 13 |
| Exactly one source. Copy book, chapter, page, and link. Do not invent them. Excerpt must be a verbatim quote. | `prompts/openai/system.txt` lines 15–19 |
| Return only JSON. | `prompts/openai/system.txt` lines 21–22; `prompts/openai/human.txt` line 8 |
| Parse JSON and validate `answer`, `confidence`, `in_scope`, and `sources`. | `apps/backend/src/rag/generator.py` lines 31–34; `apps/backend/src/rag/schemas.py` lines 16–21 |
| Turn a literal `\n`, or the words `<blank line>`, into a real paragraph break. | `apps/backend/src/rag/generator.py` lines 37–40 |
| If the answer string is empty, fill it from the citation excerpt. | `apps/backend/src/rag/generator.py` lines 32 and 100–112 |

## Check

With `LLM_OPTION=openai` (`gpt-4o`), the question “What are the biological roles of glycans?” returned an in-scope answer of about 1,000 characters in 3 paragraphs, confidence `high`. The citation was Chapter 1, Historical Background and Overview, from Essentials of Glycobiology, Fourth Edition. The excerpt was a sentence from that chapter.
