from datetime import date, timedelta
import streamlit as st

def apply_filters(noticia_service, selected_option, selected_fontes):
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
    if st.session_state['selected_subcategoria']:  # Adicionar subcategoria ao filtro
        filters_applied['SUBCATEGORIA'] = st.session_state['selected_subcategoria']
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
