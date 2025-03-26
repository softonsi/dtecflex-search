import streamlit as st
from streamlit_tags import st_tags

def render_period_and_font_filters(noticia_service):
    st.sidebar.divider()
    period_options = ["-", "Últimos 3 dias", "Últimos 5 dias", "Últimos 10 dias", "Últimos 15 dias"]

    default_option = st.session_state.get('selected_option', "-")
    default_index = period_options.index(default_option) if default_option in period_options else 0

    def update_period():
        st.session_state['selected_option'] = st.session_state['selected_option_temp']

    selected_option_temp = st.sidebar.selectbox(
        "Selecione o período:",
        options=period_options,
        index=default_index,
        key='selected_option_temp',
        on_change=update_period
    )
    st.sidebar.divider()

    fontes_options = noticia_service.get_all_fontes()
    default_fontes = st.session_state.get('selected_fontes', [])
    
    def update_fontes():
        st.session_state['selected_fontes'] = st.session_state['selected_fontes_temp']
        
    selected_fontes_temp = st.sidebar.multiselect(
        'Selecione as fontes:',
        options=fontes_options,
        default=default_fontes,
        key='selected_fontes_temp',
        on_change=update_fontes
    )
    st.sidebar.divider()

    return st.session_state['selected_option'], st.session_state['selected_fontes']

def render_categoria_filters():
    categoria_options = ['-', 'Lavagem de dinheiro', 'Ambiental', 'Crime', 'Empresarial', 'Fraude']
    current_categoria = st.session_state.get('selected_categoria', '-')
    if current_categoria not in categoria_options:
        current_categoria = '-'
        st.session_state['selected_categoria'] = '-'
    
    default_index = categoria_options.index(current_categoria) if current_categoria in categoria_options else 0

    selected_categoria_temp = st.sidebar.selectbox(
         "Selecione a categoria:",
         options=categoria_options,
         index=default_index,
         key='selected_categoria_temp'
    )
    if selected_categoria_temp == '-':
         st.session_state['selected_categoria'] = ''
    else:
         st.session_state['selected_categoria'] = selected_categoria_temp
         
    st.sidebar.divider()

def render_subcategoria_filters():
    default_subcategoria = st.session_state.get('selected_subcategoria', [])
    selected_subcategoria_temp = st_tags(
        label='Subcategoria',
        text='Digite uma subcategoria e pressione enter',
        value=default_subcategoria,
        key='selected_subcategoria_temp'
    )
    st.session_state['selected_subcategoria'] = selected_subcategoria_temp

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
    render_subcategoria_filters()
    render_status_filters()
    return selected_option, selected_fontes
