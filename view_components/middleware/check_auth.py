import streamlit as st
from functools import wraps

def check_authentication():
    return st.session_state.get('user', False)

def require_authentication(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not check_authentication():
            st.warning("Por favor, faça login para acessar esta página.")
            st.switch_page('pages/login.py')
        else:
            return func(*args, **kwargs)
    return wrapper
