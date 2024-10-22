from datetime import date, datetime, timedelta

import streamlit as st

from database import Base, SessionLocal, engine
from models.database import NoticiaRaspadaModel
from repositories.noticia_repository import NoticiaRepository
from schemas.noticia import (
    NoticiaRaspadaCreateSchema,
    NoticiaRaspadaSchema,
    NoticiaRaspadaUpdateSchema,
)
from services.noticia_service import NoticiaService

Base.metadata.create_all(bind=engine)

def main():
    st.set_page_config(layout='wide')
    st.title("Lista de Notícias")

    st.markdown(
    """
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auUHMUAnbYt6LPbKhT1Q1u1AL3LlmjMss0bGgi" crossorigin="anonymous">
    """,
    unsafe_allow_html=True,)

    session = SessionLocal()

    noticia_repository = NoticiaRepository(session)
    noticia_service = NoticiaService(noticia_repository)

    if 'edit_mode' not in st.session_state:
        st.session_state['edit_mode'] = False
    if 'edit_id' not in st.session_state:
        st.session_state['edit_id'] = None

    def listar_noticias():
        st.sidebar.header("Filtros")

        with st.sidebar.expander("Filtrar por Categoria", expanded=True):
            categoria_filter = st.selectbox('Categoria', options=['', 'Lavagem de dinheiro', 'Ambiental', 'Crime', 'Empresarial'])

        with st.sidebar.expander("Filtrar por Status", expanded=True):
            status_10_url_ok = st.checkbox("10-URL-OK")
            status_15_url_chk = st.checkbox("15-URL-CHK")
            status_99_deleted = st.checkbox("99-DELETED")
            status_07_edit = st.checkbox("07-EDIT-MODE")

        with st.sidebar.expander("Notícias por Página", expanded=True):
            per_page = st.number_input('Notícias por página', min_value=1, max_value=100, value=10)

        with st.sidebar.expander("Filtrar por Período", expanded=True):
            today = date.today()
            options = ["-", "Hoje", "Última semana", "Último mês"]
            selected_option = st.selectbox("Selecione o período:", options)

        filters = {}

        if selected_option == "Hoje":
            filters = {
                'PERIODO': 'dia',
                'DATA_INICIO': today,
                'DATA_FIM': today
            }
        elif selected_option == "Última semana":
            filters = {
                'PERIODO': 'semana',
                'DATA_INICIO': today - timedelta(days=7),
                'DATA_FIM': today
            }
        elif selected_option == "Último mês":
            filters = {
                'PERIODO': 'mes',
                'DATA_INICIO': today - timedelta(days=30),
                'DATA_FIM': today
            }
        elif selected_option == "-":
            filters = {}

        selected_status = []
        if status_10_url_ok:
            selected_status.append("10-URL-OK")
        if status_15_url_chk:
            selected_status.append("15-URL-CHK")
        if status_99_deleted:
            selected_status.append("99-DELETED")
        if status_07_edit:
            selected_status.append("07-EDIT-MODE")

        if selected_status:
            filters['STATUS'] = selected_status

        if categoria_filter:
            filters['CATEGORIA'] = categoria_filter
        if 'page_number' not in st.session_state:
            st.session_state['page_number'] = 1

        if 'last_filters' not in st.session_state:
            st.session_state['last_filters'] = filters
        elif filters != st.session_state['last_filters']:
            st.session_state['page_number'] = 1
            st.session_state['last_filters'] = filters

        noticias, total_noticias = noticia_service.listar_noticias(
            page=st.session_state['page_number'],
            per_page=per_page,
            filters=filters
        )
        total_pages = (total_noticias + per_page - 1) // per_page or 1

        cols = st.columns([10,1,1,1])
        with cols[2]:
            if st.button("Ant.", disabled=st.session_state['page_number'] <= 1):
                st.session_state['page_number'] -= 1
                st.rerun()
        with cols[1]:
            st.markdown(
                f"<div style='text-align: center; padding-top: 10px;'>{st.session_state['page_number']} - {total_pages}</div>",
                unsafe_allow_html=True
            )
        with cols[3]:
            if st.button("Próx.", disabled=st.session_state['page_number'] >= total_pages):
                st.session_state['page_number'] += 1
                st.rerun()

        if noticias:
            index = 0
            noticias_data = [noticia.model_dump() for noticia in noticias]

            for noticia in noticias_data:
                index += 1

                if index % 2 == 1:
                    background_color = "#f0f0f0"
                else:
                    background_color = "#ffffff"

                with st.container():
                    top_cols = st.columns(4)
                    with top_cols[0]:
                        st.markdown(f"**Categoria**: {noticia['CATEGORIA']}")
                    with top_cols[1]:
                        st.markdown(f"**Publicação**: {noticia['DATA_PUBLICACAO']}")
                    with top_cols[2]:
                        st.markdown(f"**Extração**: {noticia['DT_RASPAGEM']}")

                    col1, col2 = st.columns([1, 3])

                    with col1:
                        st.markdown(render_box('ID', noticia["ID"]), unsafe_allow_html=True)
                        st.markdown(render_box('Status', noticia['STATUS']), unsafe_allow_html=True)

                        if noticia['STATUS'] == '99-DELETED':
                            if st.button("Recuperar", key=f"recuperar_{noticia['ID']}_{st.session_state['page_number']}", use_container_width=True):
                                update_data = NoticiaRaspadaUpdateSchema(STATUS='15-URL-CHK')
                                noticia_service.atualizar_noticia(noticia['ID'], update_data)
                                st.toast(f"Notícia ID {noticia['ID']} recuperada com sucesso.")
                                st.rerun()
                        else:
                            if st.button("Excluir", key=f"delete_{noticia['ID']}_{st.session_state['page_number']}", use_container_width=True):
                                update_data = NoticiaRaspadaUpdateSchema(STATUS='99-DELETED')
                                noticia_service.atualizar_noticia(noticia['ID'], update_data)
                                st.toast(f"Notícia ID {noticia['ID']} excluída com sucesso.")
                                st.rerun()

                        if st.button("Analisar", key=f"analisar_{noticia['ID']}_{st.session_state['page_number']}", use_container_width=True, disabled=not (noticia['STATUS'] == '10-URL-OK' or noticia['STATUS'] == '07-EDIT-MODE') ):
                            st.session_state['id_notice_to_analyze'] = noticia['ID']
                            st.session_state[f'notice_to_analyze_{noticia['ID']}'] = noticia
                            st.session_state['url'] = noticia['URL']
                            update_data = NoticiaRaspadaUpdateSchema(STATUS='07-EDIT-MODE')
                            noticia_service.atualizar_noticia(noticia['ID'], update_data)
                            st.switch_page("pages/_extract_page.py")
                    with col2:
                        st.markdown(render_box('Fonte', noticia['FONTE']), unsafe_allow_html=True)
                        st.markdown(render_box('Título', noticia['TITULO']), unsafe_allow_html=True)
                        st.markdown(f'**Link Google:** [Acessar link]({noticia["LINK_ORIGINAL"]})')

                        key_edit_mode = f"edit_mode_{noticia['ID']}"
                        if key_edit_mode not in st.session_state:
                            st.session_state[key_edit_mode] = False

                        if noticia['URL'] is None or noticia['STATUS'] == '15-URL-CHK' or st.session_state[key_edit_mode]:
                            with st.form(key=f"link_form_{noticia['ID']}"):
                                link_col, button_col = st.columns([4, 1])
                                with link_col:
                                    link = st.text_input('**Link Notícia**', value=noticia.get('URL', ''), label_visibility="collapsed")
                                with button_col:
                                    salvar_link = st.form_submit_button('Salvar')

                                if salvar_link:
                                    if salvar_link:
                                        if not link or not link.strip():
                                            st.error("O link não pode ser vazio.")
                                        else:
                                            update_data = NoticiaRaspadaUpdateSchema(URL=link.strip(), STATUS='10-URL-OK')
                                            noticia_service.atualizar_noticia(noticia['ID'], update_data)
                                            st.toast(f"URL da notícia ID {noticia['ID']} atualizada com sucesso.")
                                            st.session_state[key_edit_mode] = False
                                            st.rerun()
                        else:
                            link_col, button_col = st.columns([4, 1])
                            with link_col:
                                st.markdown(f'**Link Notícia:** [{noticia["URL"]}]({noticia["URL"]})')
                            with button_col:
                                if st.button('Editar', key=f"edit_link_{noticia['ID']}"):
                                    st.session_state[key_edit_mode] = True
                                    st.rerun()
                    st.markdown("---")

        else:
            st.info("Nenhuma notícia encontrada.")

    def editar_noticia(noticia_id):
        noticia = noticia_service.obter_noticia(noticia_id)
        if noticia:
            st.subheader(f"Editar Notícia ID {noticia.ID}")
            with st.form(key='edit_form'):
                campos = NoticiaRaspadaUpdateSchema.__fields__.keys()
                valores = {}
                for campo in campos:
                    valor_atual = getattr(noticia, campo)
                    if isinstance(valor_atual, (datetime, date)):
                        valores[campo] = st.date_input(campo, value=valor_atual)
                    elif isinstance(valor_atual, int):
                        valores[campo] = st.number_input(campo, value=valor_atual)
                    else:
                        valores[campo] = st.text_input(campo, value=valor_atual or '')
                submit_button = st.form_submit_button(label='Salvar')
                submit_button2 = st.form_submit_button(label='Cancelar')
                if submit_button:
                    update_data = NoticiaRaspadaUpdateSchema(**valores)
                    noticia_service.atualizar_noticia(noticia.ID, update_data)
                    st.toast("Notícia atualizada com sucesso.")
                    st.session_state['edit_mode'] = False
                    st.session_state['edit_id'] = None
                    st.rerun()
                if submit_button2:
                    st.session_state['edit_mode'] = False
                    st.session_state['edit_id'] = None
                    st.rerun()
        else:
            st.error("Notícia não encontrada.")

    if st.session_state['edit_mode'] and st.session_state['edit_id']:
        editar_noticia(st.session_state['edit_id'])
    else:
        listar_noticias()

    session.close()

def render_box(txt_label, txt):
    return f"""
    <div style="
        display: flex;
        flex-direction: column;
        margin-bottom: 10px;
    ">
        <label style="
            font-size: 14px;
            color: #333;
            margin-bottom: 2px;
        ">
            {txt_label}
        </label>
        <div style="
            font-weight: bold;
            background-color: #fbfbfb;
            padding: 8px;
            border-radius: 10px;
            border: 1px solid #ccc;
            font-size: 14px;
            color: #1f77b4;
        ">
            {txt}
        </div>
    </div>
"""

def render_minibox(txt_label, txt):
    return f"""
    <div style="
        display: flex;
        flex-direction: column;
        margin-bottom: 10px;
    ">
        <label style="
            font-size: 14px;
            color: #333;
            margin-bottom: 2px;
        ">
            {txt_label}
        </label>
        <div style="
            background-color: #f9f9f9;
            padding: 0px;
            border-radius: 5px;
            border: 1px solid #ccc;
            font-size: 14px;
            color: #1f77b4;
        ">
            {txt}
        </div>
    </div>
"""

def render_status(txt_label, txt):
    if not txt:
        txt = 'SEM STATUS'

    if '99-' in txt: # Vermelho
        bg_color = '#f8d7da'
    elif '10-' in txt: # Verde
        bg_color = '#b2e6b2'
    elif '15-' in txt: # Amarelo
        bg_color = '#fff3cd'
    else: # default / neutro
        bg_color = '#fff8e1'

    return f"""
    <div style="
        display: flex;
        flex-direction: column;
        margin-bottom: 15px;
    ">
        <label style="
            font-size: 14px;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        ">
            {txt_label}
        </label>
        <div style="
            background-color: {bg_color};
            padding: 8px;
            border-radius: 5px;
            border: 1px solid #ccc;
            font-size: 14px;
            color: #1f77b4;
        ">
            {txt}
        </div>
    </div>
"""


if __name__ == "__main__":
    main()
