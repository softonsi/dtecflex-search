import streamlit as st
from streamlit_cookies_controller import CookieController

st.set_page_config('Login', layout='wide')

controller = CookieController()

cookies = controller.getAll()
if cookies is None:
    controller.refresh()

jwt_token = None
for key, value in cookies.items():
    if key == 'token':
        jwt_token = value
        break

if jwt_token:
    st.switch_page('pages/home.py')

if st.session_state.get('token') and not jwt_token:
    controller.set('token', st.session_state.get('token'))
    # st.rerun()
