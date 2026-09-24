from .base import ChatLLM
from .config import LLMOption
from .groq import create_groq_llm
from .openai import create_openai_llm


def create_chat_llm(option: LLMOption) -> ChatLLM:
    if option.provider == "groq":
        return create_groq_llm(option.model, option.temperature)
    if option.provider == "openai":
        return create_openai_llm(option.model, option.temperature)
    raise ValueError(
        f"Unsupported LLM provider {option.provider!r} for option {option.key!r}. "
        "Supported providers: groq, openai."
    )
