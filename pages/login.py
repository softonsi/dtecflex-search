import streamlit as st
from backend.resources.auth.auth_service import AuthService
from backend.resources.user.user_service import UserService

auth_service = AuthService()

def main():
    st.title('Tela de Login')

    email = st.text_input('Usuário')
    senha = st.text_input('Senha', type='password')

    if st.button('Login'):
        user_jwt = auth_service.login(email, senha)
        if user_jwt:
            st.session_state['user'] = user_jwt
            st.switch_page('pages/home.py')
        else:
            st.error('Falha no login. Verifique suas credenciais.')


if __name__ == "__main__":
    user_cookie = st.session_state.get('user', False)
    if user_cookie:
        st.switch_page('pages/home.py')

    main()