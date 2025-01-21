import streamlit as st
from backend.resources.auth.auth_service import AuthService
from database import SessionLocal
from view_components.middleware.check_auth import require_authentication

session = SessionLocal()

def main():
    st.title('Tela de Login')

    email = st.text_input('Usuário')
    senha = st.text_input('Senha', type='password')

    if st.button('Login'):
        auth_service = AuthService(session)
        user_jwt = auth_service.login(email, senha)
        if user_jwt:
            st.session_state['token'] = user_jwt
            st.session_state['log'] = False
            st.switch_page('pages/set_token.py')
        else:
            st.toast('Falha no login. Verifique suas credenciais.')


if __name__ == "__main__":
    user_cookie = st.session_state.get('user', False)
    if user_cookie:
        st.switch_page('pages/home.py')

    main()