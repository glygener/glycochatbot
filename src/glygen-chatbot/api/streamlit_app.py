import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")

from api.http_client import GlygenApiClient  # noqa: E402

st.set_page_config(
    page_title="GlyGen Chatbot",
    page_icon="🧬",
    layout="centered",
)


@st.cache_resource
def get_api_client() -> GlygenApiClient:
    return GlygenApiClient()


def ensure_session(client: GlygenApiClient) -> str:
    if "session_id" not in st.session_state:
        session = client.create_session()
        st.session_state.session_id = session["session_id"]
        st.session_state.messages = []
    return st.session_state.session_id


def load_history(client: GlygenApiClient, session_id: str) -> None:
    data = client.get_messages(session_id)
    st.session_state.messages = data["messages"]


def render_message(message: dict) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def main() -> None:
    client = get_api_client()
    api_url = os.getenv("GLYGEN_API_URL", "http://127.0.0.1:8000")

    st.title("GlyGen Chatbot")
    st.caption(f"Backend: {api_url}")

    with st.sidebar:
        if st.button("New chat", use_container_width=True):
            session = client.create_session()
            st.session_state.session_id = session["session_id"]
            st.session_state.messages = []
            st.rerun()

        st.subheader("Chats")
        try:
            sessions = client.list_sessions()
        except Exception as exc:
            st.error(f"Could not load sessions: {exc}")
            sessions = []

        current_id = st.session_state.get("session_id")

        for session in sessions:
            label = session["preview"]
            if session["session_id"] == current_id:
                label = f"• {label}"
            if st.button(label, key=f"chat_{session['session_id']}", use_container_width=True):
                st.session_state.session_id = session["session_id"]
                load_history(client, session["session_id"])
                st.rerun()

    session_id = ensure_session(client)

    if "messages" not in st.session_state:
        load_history(client, session_id)

    for message in st.session_state.messages:
        render_message(message)

    if question := st.chat_input("Ask a question..."):
        with st.chat_message("user"):
            st.markdown(question)

        with st.spinner("Thinking..."):
            try:
                result = client.chat(session_id, question)
            except Exception as exc:
                st.error(f"Something went wrong: {exc}")
                st.stop()

        with st.chat_message("assistant"):
            st.markdown(result["answer"])

        load_history(client, session_id)
        st.rerun()


if __name__ == "__main__":
    main()
