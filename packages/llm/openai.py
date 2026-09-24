import os

from langchain_openai import ChatOpenAI

from .base import ChatLLM


def create_openai_llm(model: str, temperature: float) -> ChatLLM:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY is not set. Add it to .env in the project root.")
    return ChatOpenAI(model=model, temperature=temperature, api_key=key)
