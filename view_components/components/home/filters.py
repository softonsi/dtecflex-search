from datetime import date, timedelta
import streamlit as st

def filters(st, noticia_service):
    st.sidebar.header("Filtros")

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

    with st.sidebar.expander("Filtrar por Categoria", expanded=True):
        categoria_options = ['Lavagem de dinheiro', 'Ambiental', 'Crime', 'Empresarial']

        for categoria in categoria_options:
            checkbox_key = f'categoria_{categoria}'

            if checkbox_key not in st.session_state:
                st.session_state[checkbox_key] = categoria in st.session_state['selected_categoria']

            st.checkbox(
                label=categoria,
                value=st.session_state[checkbox_key],
                key=checkbox_key,
                on_change=lambda c=categoria: update_selected_categoria(c)
            )

    with st.sidebar.expander("Filtrar por Fonte", expanded=True):
        fontes_options = noticia_service.get_all_fontes()

        selected_fontes = st.multiselect(
            'Selecione as fontes:',
            options=fontes_options,
            default=st.session_state['selected_fontes'],
            key='selected_fontes_widget'
        )

        st.session_state['selected_fontes'] = selected_fontes

    with st.sidebar.expander("Filtrar por Status", expanded=True):
        status_options = ["10-URL-OK", "15-URL-CHK", "99-DELETED", "07-EDIT-MODE"]

        for status in status_options:
            checkbox_key = f'status_{status}'

            if checkbox_key not in st.session_state:
                st.session_state[checkbox_key] = status in st.session_state['selected_status']

            st.checkbox(
                label=status,
                value=st.session_state[checkbox_key],
                key=checkbox_key,
                on_change=lambda s=status: update_selected_status(s)
            )

    # with st.sidebar.expander("Notícias por Página", expanded=True):
    #     per_page = st.number_input(
    #         'Notícias por página',
    #         min_value=1,
    #         max_value=100,
    #         value=st.session_state['per_page'],
    #         key='per_page'
    #     )

    with st.sidebar.expander("Filtrar por Período", expanded=True):
        today = date.today()
        options = ["-", "Hoje", "Última semana", "Último mês"]

        selected_option = st.selectbox(
            "Selecione o período:",
            options,
            index=options.index(st.session_state['selected_option']) if st.session_state['selected_option'] in options else 0,
            key='selected_option_widget'
        )

        st.session_state['selected_option'] = selected_option

    filters_applied = {}

    if selected_option == "Hoje":
        filters_applied.update({
            'PERIODO': 'dia',
            'DATA_INICIO': today,
            'DATA_FIM': today
        })
    elif selected_option == "Última semana":
        filters_applied.update({
            'PERIODO': 'semana',
            'DATA_INICIO': today - timedelta(days=7),
            'DATA_FIM': today
        })
    elif selected_option == "Último mês":
        filters_applied.update({
            'PERIODO': 'mes',
            'DATA_INICIO': today - timedelta(days=30),
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
