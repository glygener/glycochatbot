"""Register page — open manually at /register (not linked from login)."""

from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from browser_auth import hydrate_auth_from_browser, persist_auth
from client import GlygenApiClient

for parent in [Path(__file__).resolve().parent, *Path(__file__).resolve().parents]:
    env_file = parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        break

st.set_page_config(page_title="Register · GlyGen Chatbot", page_icon="🧬", layout="centered")


@st.cache_resource
def get_api_client() -> GlygenApiClient:
    return GlygenApiClient()


hydrate_auth_from_browser()
client = get_api_client()

st.title("Create an account")
st.caption("Choose a unique username. You can sign in with that username on the home page.")

with st.form("register_form"):
    first_name = st.text_input("First name")
    last_name = st.text_input("Last name")
    email = st.text_input("Email (Gmail)")
    username = st.text_input("Username (unique)")
    submitted = st.form_submit_button("Create account", use_container_width=True)

if submitted:
    try:
        result = client.register(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            username=username.strip(),
            email=email.strip() or None,
        )
    except Exception as exc:
        st.error(str(exc))
    else:
        st.session_state.access_token = result["access_token"]
        st.session_state.user = result["user"]
        persist_auth(result["access_token"], result["user"])
        st.session_state.pop("session_id", None)
        st.session_state.messages = []
        st.success("Account created. You are signed in — open the Home page to chat.")
        st.rerun()

if st.session_state.get("access_token") and st.session_state.get("user"):
    user = st.session_state.user
    st.info(f"Signed in as @{user['username']}. Go to **Home** to use the chatbot.")
