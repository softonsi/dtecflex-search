from datetime import date, timedelta
from backend.resources.notice.noticia_service import NoticiaService
from database import SessionLocal
import streamlit as st

session = SessionLocal()

def filters(session=session):
    noticia_service = NoticiaService(session)

    for key, default in {
        'selected_categoria': [],
        'selected_status': [],
        'selected_fontes': [],
        'per_page': 30,
        'selected_option': "-",
        'page_number': 1,
        'last_filters': {}
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    st.sidebar.divider()

    period_options = ["-", "Últimos 3 dias", "Últimos 5 dias", "Últimos 10 dias", "Últimos 15 dias"]
    selected_option = st.sidebar.selectbox(
        "Selecione o período:",
        options=period_options,
        index=period_options.index(st.session_state['selected_option']),
        key='selected_option'
    )
    st.sidebar.divider()

    fontes_options = noticia_service.get_all_fontes()
    selected_fontes = st.sidebar.multiselect(
        'Selecione as fontes:',
        options=fontes_options,
        key='selected_fontes'
    )
    st.sidebar.divider()

    def update_selected_categoria(categoria):
        if categoria in st.session_state['selected_categoria']:
            st.session_state['selected_categoria'].remove(categoria)
        else:
            st.session_state['selected_categoria'].append(categoria)

    categoria_options = ['Lavagem de dinheiro', 'Ambiental', 'Crime', 'Empresarial', 'Fraude']
    for categoria in categoria_options:
        checkbox_key = f'categoria_{categoria}'
        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = False
        st.sidebar.checkbox(
            label=categoria,
            value=st.session_state[checkbox_key],
            key=checkbox_key,
            on_change=lambda c=categoria: update_selected_categoria(c)
        )
    st.sidebar.divider()

    def update_selected_status(status):
        if status in st.session_state['selected_status']:
            st.session_state['selected_status'].remove(status)
        else:
            st.session_state['selected_status'].append(status)

    status_options = ["10-URL-OK", "15-URL-CHK", "99-DELETED"]
    for status in status_options:
        checkbox_key = f'status_{status}'
        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = False
        st.sidebar.checkbox(
            label=status,
            value=st.session_state[checkbox_key],
            key=checkbox_key,
            on_change=lambda s=status: update_selected_status(s)
        )
    st.sidebar.divider()

    filters_applied = {'STATUS': ['10-URL-OK', '15-URL-CHK']}
    today = date.today()
    period_map = {
        "Últimos 3 dias": 3,
        "Últimos 5 dias": 5,
        "Últimos 10 dias": 10,
        "Últimos 15 dias": 15
    }
    if selected_option in period_map:
        filters_applied.update({
            'PERIODO': 'dias',
            'DATA_INICIO': today - timedelta(days=period_map[selected_option]),
            'DATA_FIM': today
        })

    if st.session_state['selected_status']:
        filters_applied['STATUS'] = st.session_state['selected_status']
    if st.session_state['selected_categoria']:
        filters_applied['CATEGORIA'] = st.session_state['selected_categoria']
    if selected_fontes:
        filters_applied['FONTE'] = selected_fontes

    per_page = st.session_state.get('per_page', 30)
    if st.session_state['last_filters'] != filters_applied:
        st.session_state['page_number'] = 1
        st.session_state['last_filters'] = filters_applied

    noticias, total_noticias = noticia_service.listar_noticias(
        page=st.session_state['page_number'],
        per_page=per_page,
        filters=filters_applied
    )
    total_pages = (total_noticias + per_page - 1) // per_page or 1

    return noticias, total_pages
