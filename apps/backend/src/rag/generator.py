import json

from langchain_core.prompts import ChatPromptTemplate

from llm.prompts import load_chat_prompts
from llm.registry import create_chat_llm
from rag.config import RAGConfig
from rag.prompts import HUMAN_PROMPT, SYSTEM_PROMPT
from rag.schemas import RAGResponse


class AnswerGenerator:
    def __init__(self, config: RAGConfig) -> None:
        self.config = config
        self.llm = create_chat_llm(config.llm)
        try:
            system_prompt, human_prompt = load_chat_prompts(
                config.project_root,
                config.prompt_dir,
            )
        except FileNotFoundError:
            system_prompt, human_prompt = SYSTEM_PROMPT, HUMAN_PROMPT
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt),
        ])

    def generate(self, question: str, context: str) -> RAGResponse:
        messages = self.prompt.invoke({"context": context, "question": question})
        raw = self._message_text(self.llm.invoke(messages))
        data = self._pick_payload(raw)
        self._fill_empty_answer(data)
        return RAGResponse.model_validate(data)

    @staticmethod
    def _message_text(message) -> str:
        """Collect visible content and Groq gpt-oss reasoning text."""
        parts: list[str] = []
        content = getattr(message, "content", "")
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    for key in ("text", "content", "reasoning"):
                        value = item.get(key)
                        if isinstance(value, str):
                            parts.append(value)

        extra = getattr(message, "additional_kwargs", None) or {}
        for key in ("reasoning_content", "reasoning"):
            value = extra.get(key)
            if isinstance(value, str):
                parts.append(value)

        return "\n".join(part for part in parts if part and str(part).strip())

    @classmethod
    def _pick_payload(cls, text: str) -> dict:
        objects = cls._extract_json_objects(text)
        if not objects:
            raise ValueError("LLM did not return valid JSON.")

        candidates = [
            obj for obj in objects
            if any(key in obj for key in ("answer", "sources", "in_scope"))
        ]
        pool = candidates or objects
        pool.sort(key=lambda obj: len(str(obj.get("answer") or "").strip()), reverse=True)
        return pool[0]

    @staticmethod
    def _extract_json_objects(text: str) -> list[dict]:
        decoder = json.JSONDecoder()
        objects: list[dict] = []
        index = 0
        while True:
            start = text.find("{", index)
            if start < 0:
                break
            try:
                obj, end = decoder.raw_decode(text, start)
            except json.JSONDecodeError:
                index = start + 1
                continue
            if isinstance(obj, dict):
                objects.append(obj)
            index = end
        return objects

    @staticmethod
    def _fill_empty_answer(data: dict) -> None:
        if str(data.get("answer") or "").strip():
            return
        sources = data.get("sources") or []
        excerpts = []
        for source in sources:
            if isinstance(source, dict):
                excerpts.append(str(source.get("excerpt") or "").strip())
            else:
                excerpts.append(str(getattr(source, "excerpt", "") or "").strip())
        fallback = " ".join(part for part in excerpts if part).strip()
        if fallback:
            data["answer"] = fallback
