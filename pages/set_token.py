import streamlit as st
import time
from streamlit_cookies_controller import CookieController

st.set_page_config('Login', layout='wide')

controller = CookieController()

jwt_token = None
if st.session_state['log'] == True:
    for _ in range(4):
        token = controller.get('token')
        if token:
            jwt_token = token
            break
        time.sleep(1)

if jwt_token:
    st.switch_page('pages/home.py')

if st.session_state.get('token', False) and not st.session_state.get('log', False):
    controller.set('token', st.session_state.get('token'))
    st.session_state['log'] = True
    # st.rerun()
