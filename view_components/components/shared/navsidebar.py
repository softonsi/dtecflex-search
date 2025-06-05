import streamlit as st
from backend.resources.auth.auth_service import AuthService

def navsidebar(current_user):
    st.sidebar.markdown("#### v1.1.1")
    st.sidebar.title("Navegação")

    if current_user:
        st.sidebar.page_link("pages/home.py", label="Home")
        st.sidebar.page_link("pages/my_analysis.py", label="Minhas análises")
        if current_user['admin']:
            st.sidebar.page_link("pages/approve_notices.py", label="Aprovar notícias")
            st.sidebar.page_link("pages/user_register.py", label="Registrar usuário")
    else:
        st.sidebar.page_link("pages/login.py", label="Login")
        st.sidebar.page_link("pages/search.py", label="Pesquisa")