import streamlit as st

def render_period_and_font_filters(noticia_service):
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

    return selected_option, selected_fontes

def render_categoria_filters():
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

def render_status_filters():
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

def render_sidebar_filters(noticia_service):
    selected_option, selected_fontes = render_period_and_font_filters(noticia_service)
    render_categoria_filters()
    render_status_filters()
    return selected_option, selected_fontes
