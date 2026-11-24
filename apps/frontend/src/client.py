import os

import requests


class GlygenApiClient:
    def __init__(self, base_url: str | None = None, timeout: float = 300.0) -> None:
        self.base_url = (base_url or os.getenv("GLYGEN_API_URL", "http://127.0.0.1:8000")).rstrip("/")
        self.timeout = timeout or 300.0
        self.token: str | None = None

    def set_token(self, token: str | None) -> None:
        self.token = token

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _headers(self, auth: bool = False) -> dict[str, str]:
        headers: dict[str, str] = {}
        if auth:
            if not self.token:
                raise RuntimeError("Not logged in.")
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def health(self) -> dict:
        response = requests.get(self._url("/health"), timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def register(
        self,
        first_name: str,
        last_name: str,
        username: str,
        email: str | None = None,
    ) -> dict:
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
        }
        if email:
            payload["email"] = email
        response = requests.post(
            self._url("/api/v1/auth/register"),
            json=payload,
            timeout=15,
        )
        if response.status_code >= 400:
            detail = response.json().get("detail", response.text)
            raise RuntimeError(detail)
        return response.json()

    def login(self, username: str, browser_id: str | None = None) -> dict:
        payload: dict = {"username": username}
        if browser_id:
            payload["browser_id"] = browser_id
        response = requests.post(
            self._url("/api/v1/auth/login"),
            json=payload,
            timeout=15,
        )
        if response.status_code >= 400:
            detail = response.json().get("detail", response.text)
            raise RuntimeError(detail)
        return response.json()

    def me(self) -> dict:
        response = requests.get(
            self._url("/api/v1/auth/me"),
            headers=self._headers(auth=True),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def create_session(self) -> dict:
        response = requests.post(
            self._url("/api/v1/sessions"),
            headers=self._headers(auth=True),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def list_sessions(self) -> list[dict]:
        response = requests.get(
            self._url("/api/v1/sessions"),
            headers=self._headers(auth=True),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def delete_session(self, session_id: str) -> dict:
        response = requests.delete(
            self._url(f"/api/v1/sessions/{session_id}"),
            headers=self._headers(auth=True),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def get_messages(self, session_id: str) -> dict:
        response = requests.get(
            self._url(f"/api/v1/sessions/{session_id}/messages"),
            headers=self._headers(auth=True),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def chat(self, session_id: str, question: str) -> dict:
        response = requests.post(
            self._url("/api/v1/chat"),
            headers=self._headers(auth=True),
            json={"session_id": session_id, "question": question},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
