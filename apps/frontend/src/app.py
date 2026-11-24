import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from browser_auth import clear_auth, hydrate_auth_from_browser, persist_auth
from client import GlygenApiClient

for parent in [Path(__file__).resolve().parent, *Path(__file__).resolve().parents]:
    env_file = parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        break

st.set_page_config(
    page_title="GlyGen Chatbot",
    page_icon="🧬",
    layout="centered",
)


@st.cache_resource
def get_api_client() -> GlygenApiClient:
    return GlygenApiClient()


def render_login(client: GlygenApiClient) -> None:
    st.title("GlyGen Chatbot")
    st.caption("Sign in with your username.")

    with st.form("login_form"):
        username = st.text_input("Username")
        submitted = st.form_submit_button("Sign in", use_container_width=True)
    if submitted:
        try:
            result = client.login(
                username.strip(),
                browser_id=st.session_state.get("browser_id"),
            )
        except Exception as exc:
            st.error(str(exc))
        else:
            st.session_state.access_token = result["access_token"]
            st.session_state.user = result["user"]
            persist_auth(result["access_token"], result["user"])
            st.session_state.pop("session_id", None)
            st.session_state.messages = []
            st.rerun()


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


def render_chat(client: GlygenApiClient) -> None:
    user = st.session_state.user
    api_url = os.getenv("GLYGEN_API_URL", "http://127.0.0.1:8000")

    st.title(f"Hello, {user['first_name']}!")
    st.caption(f"Signed in as @{user['username']} · Backend: {api_url}")

    with st.sidebar:
        st.write(f"**{user['first_name']} {user['last_name']}**")
        st.caption(f"@{user['username']}")
        if st.button("Log out", use_container_width=True):
            clear_auth()
            st.rerun()

        if st.button("New chat", use_container_width=True):
            session = client.create_session()
            st.session_state.session_id = session["session_id"]
            st.session_state.messages = []
            st.rerun()

        st.subheader("Your chats")
        try:
            sessions = client.list_sessions()
        except Exception as exc:
            st.error(f"Could not load sessions: {exc}")
            sessions = []

        current_id = st.session_state.get("session_id")
        for session in sessions:
            cols = st.columns([4, 1])
            label = session["preview"]
            if session["session_id"] == current_id:
                label = f"• {label}"
            with cols[0]:
                if st.button(
                    label,
                    key=f"chat_{session['session_id']}",
                    use_container_width=True,
                ):
                    st.session_state.session_id = session["session_id"]
                    load_history(client, session["session_id"])
                    st.rerun()
            with cols[1]:
                if st.button("🗑", key=f"del_{session['session_id']}", help="Delete chat"):
                    client.delete_session(session["session_id"])
                    if st.session_state.get("session_id") == session["session_id"]:
                        st.session_state.pop("session_id", None)
                        st.session_state.messages = []
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


def main() -> None:
    hydrate_auth_from_browser()
    client = get_api_client()

    token = st.session_state.get("access_token")
    if token and "user" in st.session_state:
        client.set_token(token)
        try:
            me = client.me()
            st.session_state.user = me
            persist_auth(token, me)
        except Exception:
            clear_auth()
            render_login(client)
            return
        render_chat(client)
        return

    render_login(client)


if __name__ == "__main__":
    main()
