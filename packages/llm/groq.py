import os

from langchain_groq import ChatGroq

from .base import ChatLLM


def create_groq_llm(model: str, temperature: float) -> ChatLLM:
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("GROQ_API_KEY is not set. Add it to .env in the project root.")
    kwargs = {}
    if "gpt-oss" in model:
        # Keep reasoning short so the answer is returned in the message body.
        kwargs["reasoning_effort"] = "low"
    return ChatGroq(model=model, temperature=temperature, groq_api_key=key, **kwargs)
