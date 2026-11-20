import streamlit as st


def init_session() -> None:
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "user" not in st.session_state:
        st.session_state.user = None


def set_session(token: str, user: dict) -> None:
    st.session_state.access_token = token
    st.session_state.user = user


def clear_session() -> None:
    st.session_state.access_token = None
    st.session_state.user = None


def is_authenticated() -> bool:
    return bool(st.session_state.get("access_token"))


def get_token() -> str | None:
    return st.session_state.get("access_token")


def get_user() -> dict | None:
    return st.session_state.get("user")


def get_role() -> str | None:
    user = get_user()
    return user.get("Rol") if user else None