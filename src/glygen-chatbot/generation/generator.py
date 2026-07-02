import json
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from generation.prompts import HUMAN_PROMPT, SYSTEM_PROMPT
from generation.schemas import RAGResponse
from query.config import RAGConfig


class AnswerGenerator:
    def __init__(self, config: RAGConfig) -> None:
        self.config = config
        self.llm = ChatGroq(
            model=config.llm_model,
            temperature=config.temperature,
            groq_api_key=config.groq_api_key,
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", HUMAN_PROMPT),
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
