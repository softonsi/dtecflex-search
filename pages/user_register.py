import streamlit as st
from argon2 import PasswordHasher
from database import SessionLocal
from backend.resources.user.user_service import UserService
from backend.resources.user.user_repository import UserRepository
from backend.resources.user.user_schema import UserCreateBaseSchema
from view_components.components.shared.navsidebar import navsidebar

def main():
    st.set_page_config(page_title="Registro de Usuário", layout="centered")
    st.title("Registro de Usuário")
    navsidebar()
    # Inicializa o UserService
    session = SessionLocal()
    user_repository = UserRepository(session)
    user_service = UserService(user_repository)

    # Formulário de registro
    with st.form(key='registration_form'):
        username = st.text_input("Nome de Usuário")
        password = st.text_input("Senha", type="password")
        confirm_password = st.text_input("Confirme a Senha", type="password")
        admin = st.toggle("Usuário Admin", key="admin_toggle", value=False)

        submit_button = st.form_submit_button(label='Registrar')

    if submit_button:
        if not username or not password or not confirm_password:
            st.error("Por favor, preencha todos os campos.")
        elif password != confirm_password:
            st.error("As senhas não correspondem.")
        else:
            try:
                # Chama o método create do UserService
                user_service.create(username=username, pwd=password, admin=admin)
                st.success(f"Usuário '{username}' registrado com sucesso.")
            except ValueError as e:
                st.error(f"Erro no registro: {str(e)}")
            except Exception as e:
                st.error(f"Ocorreu um erro: {str(e)}")

if __name__ == "__main__":
    main()
