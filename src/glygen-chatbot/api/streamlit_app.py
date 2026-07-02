import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")
sys.path.insert(0, str(PROJECT_ROOT / "src" / "glygen-chatbot"))

from api.orchestrator import ChatOrchestrator  # noqa: E402
from RAG.pipeline import RAGPipeline  # noqa: E402
from session.store import SessionStore  # noqa: E402

st.set_page_config(
    page_title="GlyGen Chatbot",
    page_icon="🧬",
    layout="centered",
)


@st.cache_resource
def get_orchestrator() -> ChatOrchestrator:
    return ChatOrchestrator(RAGPipeline(), SessionStore())


def ensure_session(store: SessionStore) -> str:
    if "session_id" not in st.session_state:
        session = store.create_session()
        st.session_state.session_id = session.id
        st.session_state.messages = []
    return st.session_state.session_id


def load_history(orchestrator: ChatOrchestrator, session_id: str) -> None:
    data = orchestrator.get_session_messages(session_id)
    st.session_state.messages = [message.model_dump() for message in data.messages]


def render_message(message: dict) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def main() -> None:
    orchestrator = get_orchestrator()
    store = orchestrator.store

    st.title("GlyGen Chatbot")

    with st.sidebar:
        if st.button("New chat", use_container_width=True):
            session = store.create_session()
            st.session_state.session_id = session.id
            st.session_state.messages = []
            st.rerun()

        st.subheader("Chats")
        sessions = store.list_sessions()
        current_id = st.session_state.get("session_id")

        for session in sessions:
            label = session.preview
            if session.id == current_id:
                label = f"• {label}"
            if st.button(label, key=f"chat_{session.id}", use_container_width=True):
                st.session_state.session_id = session.id
                load_history(orchestrator, session.id)
                st.rerun()

    session_id = ensure_session(store)

    if "messages" not in st.session_state:
        load_history(orchestrator, session_id)

    for message in st.session_state.messages:
        render_message(message)

    if question := st.chat_input("Ask a question..."):
        with st.chat_message("user"):
            st.markdown(question)

        with st.spinner("Thinking..."):
            try:
                result = orchestrator.chat(session_id, question)
            except Exception as exc:
                st.error(f"Something went wrong: {exc}")
                st.stop()

        with st.chat_message("assistant"):
            st.markdown(result.answer)

        load_history(orchestrator, session_id)
        st.rerun()


if __name__ == "__main__":
    main()
