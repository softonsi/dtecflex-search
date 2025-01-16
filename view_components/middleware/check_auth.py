import streamlit as st
from functools import wraps
from backend.resources.auth.auth_service import AuthService
from streamlit_cookies_controller import CookieController
import time
from database import SessionLocal

session = SessionLocal()
def require_authentication(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        controller = CookieController()
        
        token = None
        for _ in range(4):
            token = controller.get('token')
            if token:
                break
            time.sleep(1)

        if not token:
            st.warning("Por favor, faça login para acessar esta página.")
            st.switch_page('pages/login.py')
            # st.rerun()
        else:
            auth_service = AuthService(session)
            decoded_user = auth_service.decode_jwt(token)
            if not decoded_user:
                st.warning("Token inválido ou expirado. Por favor, faça login novamente.")
                st.switch_page('pages/login.py')
                # st.rerun()
            else:
                return func(*args, current_user=decoded_user, **kwargs)

    return wrapper
