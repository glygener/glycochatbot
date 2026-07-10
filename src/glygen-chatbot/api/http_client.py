import os

import requests


class GlygenApiClient:
    def __init__(self, base_url: str | None = None, timeout: float = 120.0) -> None:
        self.base_url = (base_url or os.getenv("GLYGEN_API_URL", "http://127.0.0.1:8000")).rstrip("/")
        self.timeout = timeout

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def health(self) -> dict:
        response = requests.get(self._url("/health"), timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def create_session(self) -> dict:
        response = requests.post(self._url("/api/v1/sessions"), timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def list_sessions(self) -> list[dict]:
        response = requests.get(self._url("/api/v1/sessions"), timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_messages(self, session_id: str) -> dict:
        response = requests.get(
            self._url(f"/api/v1/sessions/{session_id}/messages"),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def chat(self, session_id: str, question: str) -> dict:
        response = requests.post(
            self._url("/api/v1/chat"),
            json={"session_id": session_id, "question": question},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
