import streamlit as st
from backend.resources.notice.noticia_service import NoticiaService
from database import SessionLocal
from view_components.components.home.filters.filter_logic import apply_filters
from view_components.components.home.filters.session_defaults import init_session_state
from view_components.components.home.filters.sidebar_filters import render_sidebar_filters

def filters():
    session = SessionLocal()

    init_session_state()

    noticia_service = NoticiaService(session)
    
    selected_option, selected_fontes = render_sidebar_filters(noticia_service)
    
    noticias, total_pages = apply_filters(noticia_service, selected_option, selected_fontes)

    session.close()
    
    return noticias, total_pages

if __name__ == "__main__":
    noticias, total_pages = filters()
    st.write(noticias)
    st.write("Total pages:", total_pages)
