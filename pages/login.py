import streamlit as st
from backend.resources.auth.auth_service import AuthService
from backend.exceptions.auth_exceptions import AuthenticationError
from database import SessionLocal

session = SessionLocal()

def main():
    st.title('Tela de Login')

    username = st.text_input('Usuário')
    senha = st.text_input('Senha', type='password')

    if st.button('Login'):
        auth_service = AuthService(session)
        try:
            token = auth_service.login(username, senha)
            st.session_state['token'] = token
            st.session_state['log'] = False
            st.switch_page('pages/set_token.py')
        except AuthenticationError as ae:
            st.error(str(ae))
        except Exception as e:
            st.error("Ocorreu um erro ao fazer login.")

if __name__ == "__main__":
    user_cookie = st.session_state.get('user', False)
    if user_cookie:
        st.switch_page('pages/home.py')

    main()
