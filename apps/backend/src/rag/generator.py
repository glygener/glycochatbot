import json
import re

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
        raw = self.llm.invoke(messages).content
        data = json.loads(self._extract_json(str(raw)))
        return RAGResponse.model_validate(data)

    @staticmethod
    def _extract_json(text: str) -> str:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("LLM did not return valid JSON.")
        return match.group(0)
