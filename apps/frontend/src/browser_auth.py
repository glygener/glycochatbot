"""Persist login in the browser until the user logs out."""

from __future__ import annotations

import json
import uuid

import streamlit as st
import streamlit.components.v1 as components

AUTH_KEY = "glyco_auth"
BROWSER_KEY = "glyco_browser_id"


def _ensure_browser_id() -> str:
    if st.session_state.get("browser_id"):
        return st.session_state.browser_id
    browser_id = str(uuid.uuid4())
    st.session_state.browser_id = browser_id
    return browser_id


def hydrate_auth_from_browser() -> None:
    """Load token/user from localStorage into session_state once per tab."""
    params = st.query_params

    browser_id = params.get("glyco_browser_id")
    if browser_id:
        st.session_state.browser_id = browser_id

    raw = params.get("glyco_auth")
    if raw and "access_token" not in st.session_state:
        try:
            data = json.loads(raw)
            if data.get("access_token") and data.get("user"):
                st.session_state.access_token = data["access_token"]
                st.session_state.user = data["user"]
        except (json.JSONDecodeError, TypeError, KeyError):
            pass

    # Strip secrets from the address bar after reading.
    dirty = False
    for key in ("glyco_auth", "glyco_browser_id"):
        if key in params:
            del st.query_params[key]
            dirty = True

    if st.session_state.get("_auth_hydrated"):
        if not st.session_state.get("browser_id"):
            _ensure_browser_id()
        return

    # One-time bridge: copy localStorage into the URL, then Python reads it above.
    components.html(
        f"""
        <script>
        (function() {{
          if (window.sessionStorage.getItem("glyco_hydrated") === "1") {{
            return;
          }}
          window.sessionStorage.setItem("glyco_hydrated", "1");
          let browserId = localStorage.getItem("{BROWSER_KEY}");
          if (!browserId) {{
            browserId = crypto.randomUUID();
            localStorage.setItem("{BROWSER_KEY}", browserId);
          }}
          const raw = localStorage.getItem("{AUTH_KEY}");
          const url = new URL(window.parent.location.href);
          url.searchParams.set("glyco_browser_id", browserId);
          if (raw) {{
            url.searchParams.set("glyco_auth", raw);
          }}
          window.parent.location.replace(url.toString());
        }})();
        </script>
        """,
        height=0,
    )
    st.session_state._auth_hydrated = True
    if not st.session_state.get("browser_id"):
        _ensure_browser_id()
    if dirty:
        st.rerun()


def persist_auth(token: str, user: dict) -> None:
    payload = json.dumps({"access_token": token, "user": user})
    browser_id = st.session_state.get("browser_id") or _ensure_browser_id()
    components.html(
        f"""
        <script>
        localStorage.setItem("{AUTH_KEY}", {json.dumps(payload)});
        localStorage.setItem("{BROWSER_KEY}", {json.dumps(browser_id)});
        window.sessionStorage.setItem("glyco_hydrated", "1");
        </script>
        """,
        height=0,
    )


def clear_auth() -> None:
    components.html(
        f"""
        <script>
        localStorage.removeItem("{AUTH_KEY}");
        window.sessionStorage.removeItem("glyco_hydrated");
        </script>
        """,
        height=0,
    )
    for key in ("access_token", "user", "session_id", "messages", "_auth_hydrated"):
        st.session_state.pop(key, None)
