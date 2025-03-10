import streamlit as st

def init_session_state():
    defaults = {
        'selected_categoria': [],
        'selected_status': [],
        'selected_fontes': [],
        'per_page': 30,
        'selected_option': "-",
        'page_number': 1,
        'last_filters': {}
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default
