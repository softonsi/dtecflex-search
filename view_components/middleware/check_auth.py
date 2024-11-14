import streamlit as st
from functools import wraps
from backend.resources.auth.auth_service import AuthService

def require_authentication(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = st.session_state.get('user')
        if not token:
            st.warning("Por favor, faça login para acessar esta página.")
            st.switch_page('pages/login.py')
            # st.rerun()
        else:
            auth_service = AuthService()
            decoded_user = auth_service.decode_jwt(token)
            if not decoded_user:
                st.warning("Token inválido ou expirado. Por favor, faça login novamente.")
                st.switch_page('pages/login.py')
                # st.rerun()
            else:
                return func(*args, current_user=decoded_user, **kwargs)
    return wrapper
