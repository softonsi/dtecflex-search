import streamlit as st
from view_components.middleware.check_auth import require_authentication
from database import Base, engine

from backend.models.database import NoticiaRaspadaModel, NoticiaRaspadaNomeModel, UsuarioModel

Base.metadata.create_all(bind=engine)

@require_authentication
def main():
    pass

if __name__ == "__main__":
    user_cookie = st.session_state.get('user', False)
    if user_cookie:
        st.switch_page('pages/home.py')
    elif not user_cookie:
        st.switch_page('pages/login.py')

    main()
