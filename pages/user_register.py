import streamlit as st
from database import SessionLocal
from backend.resources.user.user_service import UserService
from view_components.components.shared.navsidebar import navsidebar
from view_components.middleware.check_auth import require_authentication

@require_authentication
def main(current_user=None):
    st.set_page_config(page_title="Registro e Gerenciamento de Usuário", layout="centered")
    st.title("Registro e Gerenciamento de Usuário")
    navsidebar(current_user)
    
    session = SessionLocal()
    user_service = UserService(session)
    
    st.subheader("Registrar Novo Usuário")
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
    
    try:
        users = user_service.find_all()
    except Exception as e:
        st.error(f"Erro ao recuperar usuários: {str(e)}")
        users = []
    
    if users:
        st.subheader("Alterar Usuário")
        with st.form(key='update_form'):
            selected_user = st.selectbox(
                "Selecione o usuário para alterar", 
                options=users, 
                format_func=lambda u: f"{u.USERNAME}"
            )
            new_username = st.text_input("Novo Nome de Usuário", value=selected_user.USERNAME)
            new_password = st.text_input("Nova Senha (deixe em branco para manter a senha atual)", type="password")
            if new_password:
                confirm_new_password = st.text_input("Confirme a Nova Senha", type="password")
            else:
                confirm_new_password = ""
            new_admin = st.toggle("Usuário administrador", value=selected_user.ADMIN)
            update_submit = st.form_submit_button("Alterar Usuário")
    
            if update_submit:
                if new_password and new_password != confirm_new_password:
                    st.error("As senhas não correspondem.")
                else:
                    try:
                        user_service.update(
                            user_id=selected_user.ID,
                            username=new_username,
                            pwd=new_password if new_password else None,
                            admin=new_admin
                        )
                        st.success("Usuário atualizado com sucesso.")
                    except Exception as e:
                        st.error(f"Erro ao atualizar usuário: {str(e)}")
    
        st.subheader("Excluir Usuário")
        with st.form(key='delete_form'):
            selected_user_to_delete = st.selectbox(
                "Selecione o usuário para excluir", 
                options=users, 
                format_func=lambda u: f"{u.USERNAME}",
                key="delete_select"
            )
            delete_submit = st.form_submit_button("Excluir Usuário")
    
            if delete_submit:
                if selected_user_to_delete.ID == current_user['user_id']:
                    st.error("Você não pode excluir a si mesmo.")
                else:
                    try:
                        user_service.delete(user_id=selected_user_to_delete.ID)
                        st.success("Usuário excluído com sucesso.")
                    except Exception as e:
                        st.error(f"Erro ao excluir usuário: {str(e)}")
    else:
        st.info("Nenhum usuário cadastrado para gerenciamento.")

if __name__ == "__main__":
    main()
