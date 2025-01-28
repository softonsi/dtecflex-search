from datetime import date, timedelta
from backend.resources.notice.noticia_service import NoticiaService
from database import  SessionLocal
import streamlit as st

session = SessionLocal()
noticia_service = NoticiaService(session)

def filters(st):

    st.sidebar.divider()

    def update_selected_categoria(categoria):
        if categoria in st.session_state['selected_categoria']:
            st.session_state['selected_categoria'].remove(categoria)
        else:
            st.session_state['selected_categoria'].append(categoria)

    def update_selected_status(status):
        if status in st.session_state['selected_status']:
            st.session_state['selected_status'].remove(status)
        else:
            st.session_state['selected_status'].append(status)

    if 'selected_categoria' not in st.session_state:
        st.session_state['selected_categoria'] = []

    if 'selected_status' not in st.session_state:
        st.session_state['selected_status'] = []

    if 'selected_fontes' not in st.session_state:
        st.session_state['selected_fontes'] = []

    if 'per_page' not in st.session_state:
        st.session_state['per_page'] = 30

    if 'selected_option' not in st.session_state:
        st.session_state['selected_option'] = "-"

    if 'page_number' not in st.session_state:
        st.session_state['page_number'] = 1

    if 'last_filters' not in st.session_state:
        st.session_state['last_filters'] = {}

    # Filtro de Período
    today = date.today()
    options = ["-", "Últimos 3 dias", "Últimos 5 dias", "Últimos 10 dias", "Últimos 15 dias"]

    selected_option = st.sidebar.selectbox(
        "Selecione o período:",
        options,
        index=options.index(st.session_state['selected_option']) if st.session_state['selected_option'] in options else 0,
        key='selected_option_widget'
    )

    st.session_state['selected_option'] = selected_option
    st.sidebar.divider()

    # Filtro de Categoria
    categoria_options = ['Lavagem de dinheiro', 'Ambiental', 'Crime', 'Empresarial', 'Fraude']
    
    for categoria in categoria_options:
        checkbox_key = f'categoria_{categoria}'

        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = categoria in st.session_state['selected_categoria']

        st.sidebar.checkbox(
            label=categoria,
            value=st.session_state[checkbox_key],
            key=checkbox_key,
            on_change=lambda c=categoria: update_selected_categoria(c)
        )

    st.sidebar.divider()  # Adiciona um divisor após o filtro de categoria

    # Filtro de Fontes
    fontes_options = noticia_service.get_all_fontes()

    selected_fontes = st.sidebar.multiselect(
        'Selecione as fontes:',
        options=fontes_options,
        default=st.session_state['selected_fontes'],
        key='selected_fontes_widget'
    )

    st.session_state['selected_fontes'] = selected_fontes
    st.sidebar.divider()  # Adiciona um divisor após o filtro de fontes

    # Filtro de Status
    status_options = ["10-URL-OK", "15-URL-CHK", "99-DELETED"]

    for status in status_options:
        checkbox_key = f'status_{status}'

        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = status in st.session_state['selected_status']

        st.sidebar.checkbox(
            label=status,
            value=st.session_state[checkbox_key],
            key=checkbox_key,
            on_change=lambda s=status: update_selected_status(s)
        )

    st.sidebar.divider()  # Adiciona um divisor após o filtro de status

    filters_applied = {'STATUS': ['10-URL-OK', '15-URL-CHK']}

    if selected_option == "Últimos 3 dias":
        filters_applied.update({
            'PERIODO': 'dias',
            'DATA_INICIO': today - timedelta(days=3),
            'DATA_FIM': today
        })
    elif selected_option == "Últimos 5 dias":
        filters_applied.update({
            'PERIODO': 'dias',
            'DATA_INICIO': today - timedelta(days=5),
            'DATA_FIM': today
        })
    elif selected_option == "Últimos 10 dias":
        filters_applied.update({
            'PERIODO': 'dias',
            'DATA_INICIO': today - timedelta(days=10),
            'DATA_FIM': today
        })
    elif selected_option == "Últimos 15 dias":
        filters_applied.update({
            'PERIODO': 'dias',
            'DATA_INICIO': today - timedelta(days=15),
            'DATA_FIM': today
        })

    if st.session_state.get('selected_status'):
        filters_applied['STATUS'] = st.session_state['selected_status']

    if st.session_state.get('selected_categoria'):
        filters_applied['CATEGORIA'] = st.session_state['selected_categoria']

    if st.session_state.get('selected_fontes'):
        filters_applied['FONTE'] = st.session_state['selected_fontes']

    if st.session_state.get('per_page'):
        per_page = st.session_state['per_page']
    else:
        per_page = 30

    if 'last_filters' not in st.session_state:
        st.session_state['last_filters'] = filters_applied
    elif filters_applied != st.session_state['last_filters']:
        st.session_state['page_number'] = 1
        st.session_state['last_filters'] = filters_applied

    noticias, total_noticias = noticia_service.listar_noticias(
        page=st.session_state['page_number'],
        per_page=per_page,
        filters=filters_applied
    )
    total_pages = (total_noticias + per_page - 1) // per_page or 1

    return noticias, total_pages
