import streamlit as st

from backend.resources.auth.auth_service import AuthService

def navsidebar():
    token = st.session_state.get('user', False)

    st.sidebar.title("Navegação")

    auth_service = AuthService()
    decoded_user = auth_service.decode_jwt(token)

    if token:
        st.sidebar.page_link("pages/home.py", label="Home")
        if decoded_user['admin']:
            st.sidebar.page_link("pages/approve_notices.py", label="Aprovar notícias")
    else:
        st.sidebar.page_link("pages/login.py", label="🔐 Login")