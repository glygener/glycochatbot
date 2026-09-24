from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ChatLLM(Protocol):
    """Minimal chat interface used by answer generation."""

    def invoke(self, messages: Any) -> Any:
        ...
