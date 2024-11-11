import streamlit as st

def navsidebar():
    user_cookie = st.session_state.get('user', False)

    st.sidebar.title("Navegação")

    if user_cookie:
        st.sidebar.page_link("pages/home.py", label="🏠 Home")
    else:
        st.sidebar.page_link("pages/login.py", label="🔐 Login")