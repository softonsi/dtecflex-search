import streamlit as st
from database import SessionLocal
from backend.resources.user.user_service import UserService
from view_components.components.shared.navsidebar import navsidebar
from view_components.middleware.check_auth import require_authentication

@require_authentication
def main(current_user=None):
    st.set_page_config(page_title="Registro de Usuário", layout="centered")
    st.title("Registro de Usuário")
    navsidebar(current_user)
    session = SessionLocal()
    user_service = UserService(session)

    with st.form(key='registration_form'):
        username = st.text_input("Nome de Usuário")
        password = st.text_input("Senha", type="password")
        confirm_password = st.text_input("Confirme a Senha", type="password")
        admin = st.toggle("Usuário administrador", key="admin_toggle", value=False)

        submit_button = st.form_submit_button(label='Registrar')

    if submit_button:
        if not username or not password or not confirm_password:
            st.error("Por favor, preencha todos os campos.")
        elif password != confirm_password:
            st.error("As senhas não correspondem.")
        else:
            try:
                user_service.create(username=username, pwd=password, admin=admin)
                st.success(f"Usuário '{username}' registrado com sucesso.")
            except ValueError as e:
                st.error(f"Erro no registro: {str(e)}")
            except Exception as e:
                st.error(f"Ocorreu um erro: {str(e)}")

if __name__ == "__main__":
    main()
