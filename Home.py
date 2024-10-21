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

# Criando as tabelas no banco de dados (se ainda não existirem)
Base.metadata.create_all(bind=engine)

# Função principal da aplicação
def main():
    st.set_page_config(layout='wide')
    st.title("Lista de Notícias")

    st.markdown(
    """
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auUHMUAnbYt6LPbKhT1Q1u1AL3LlmjMss0bGgi" crossorigin="anonymous">
    """,
    unsafe_allow_html=True,)

    # Criando a sessão do banco de dados
    session = SessionLocal()

    # Inicializando o repositório e o serviço
    noticia_repository = NoticiaRepository(session)
    noticia_service = NoticiaService(noticia_repository)

    # Estado para controlar edição
    if 'edit_mode' not in st.session_state:
        st.session_state['edit_mode'] = False
    if 'edit_id' not in st.session_state:
        st.session_state['edit_id'] = None

    # Função para listar as notícias
    # Permitir que o usuário escolha o número de notícias a exibir

    def listar_noticias():
    # Campos de entrada para filtros na barra lateral
        st.sidebar.header("Filtros")

        with st.sidebar.expander("Filtrar por Categoria", expanded=True):
            categoria_filter = st.selectbox('Categoria', options=['', 'Lavagem de dinheiro', 'Ambiental', 'Crime', 'Empresarial'])

        with st.sidebar.expander("Filtrar por Status", expanded=True):
            status_10_url_ok = st.checkbox("10-URL-OK")
            status_15_url_chk = st.checkbox("15-URL-CHK")
            status_99_deleted = st.checkbox("99-DELETED")

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

        # Atualizando os filtros de status
        selected_status = []
        if status_10_url_ok:
            selected_status.append("10-URL-OK")
        if status_15_url_chk:
            selected_status.append("15-URL-CHK")
        if status_99_deleted:
            selected_status.append("99-DELETED")

        if selected_status:
            filters['STATUS'] = selected_status

        if categoria_filter:
            filters['CATEGORIA'] = categoria_filter
        if 'page_number' not in st.session_state:
            st.session_state['page_number'] = 1

        # Resetar a página se os filtros mudarem
        if 'last_filters' not in st.session_state:
            st.session_state['last_filters'] = filters
        elif filters != st.session_state['last_filters']:
            st.session_state['page_number'] = 1
            st.session_state['last_filters'] = filters

        # Obtendo as notícias filtradas
        noticias, total_noticias = noticia_service.listar_noticias(
            page=st.session_state['page_number'],
            per_page=per_page,
            filters=filters
        )
        total_pages = (total_noticias + per_page - 1) // per_page or 1

        # Botões de paginação
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

                        if st.button("Analisar", key=f"analisar_{noticia['ID']}_{st.session_state['page_number']}", use_container_width=True, disabled=noticia['STATUS'] != '10-URL-OK'):
                            print(type(noticia))
                            st.session_state['id_notice_to_analyze'] = noticia['ID']
                            st.session_state[f'notice_to_analyze_{noticia['ID']}'] = noticia
                            print(noticia['URL'])
                            st.session_state['url'] = noticia['URL']
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

    # def listar_noticias():
    #     # Campos de entrada para filtros na barra lateral
    #     st.sidebar.header("Filtros")

    #     categoria_filter = st.sidebar.selectbox('Categoria', options=['', 'Lavagem de dinheiro', 'Ambiental', 'Crime', 'Empresarial'])
    #     status_filter = st.sidebar.selectbox('Status', options=['', '10-URL-OK', '15-URL-CHK', '99-DELETED'])
    #     per_page = st.sidebar.number_input('Notícias por página', min_value=1, max_value=100, value=10)
    #     status_10_url_ok = st.sidebar.checkbox("10-URL-OK")
    #     status_15_url_chk = st.sidebar.checkbox("15-URL-CHK")
    #     status_99_deleted = st.sidebar.checkbox("99-DELETED")

    #     st.sidebar.markdown("---")
    #     st.sidebar.subheader("Filtre as notícias por periodo:")

    #     today = date.today()
    #     options = ["-", "Hoje", "Última semana", "Último mês"]
    #     selected_option = st.sidebar.selectbox("Selecione o período:", options)

    #     filters = {}

    #     if selected_option == "Hoje":
    #         filters = {
    #             'PERIODO': 'dia',
    #             'DATA_INICIO': today,
    #             'DATA_FIM': today
    #         }
    #     elif selected_option == "Última semana":
    #         filters = {
    #             'PERIODO': 'semana',
    #             'DATA_INICIO': today - timedelta(days=7),
    #             'DATA_FIM': today
    #         }
    #     elif selected_option == "Último mês":
    #         filters = {
    #             'PERIODO': 'mes',
    #             'DATA_INICIO': today - timedelta(days=30),
    #             'DATA_FIM': today
    #         }
    #     elif selected_option == "-":
    #         filters = {}

    #     st.sidebar.markdown("---")
    #     st.sidebar.subheader("Filtre as notícias por status:")

    #     st.sidebar.markdown("---")

    #     selected_status = []
    #     if status_10_url_ok:
    #         selected_status.append("10-URL-OK")
    #     if status_15_url_chk:
    #         selected_status.append("15-URL-CHK")
    #     if status_99_deleted:
    #         selected_status.append("99-DELETED")

    #     if selected_status:
    #         filters['STATUS'] = selected_status

    #     if status_filter:
    #         filters['STATUS'] = status_filter
    #     if categoria_filter:
    #         filters['CATEGORIA'] = categoria_filter
    #     if 'page_number' not in st.session_state:
    #         st.session_state['page_number'] = 1

    #     # Resetar a página se os filtros mudarem
    #     if 'last_filters' not in st.session_state:
    #         st.session_state['last_filters'] = filters
    #     elif filters != st.session_state['last_filters']:
    #         st.session_state['page_number'] = 1
    #         st.session_state['last_filters'] = filters

    #     noticias, total_noticias = noticia_service.listar_noticias(
    #         page=st.session_state['page_number'],
    #         per_page=per_page,
    #         filters=filters
    #     )
    #     total_pages = (total_noticias + per_page - 1) // per_page or 1


    #     # Botões de paginação
    #     cols = st.columns(3)
    #     with cols[0]:
    #         if st.button("Anterior", disabled=st.session_state['page_number'] <= 1):
    #             st.session_state['page_number'] -= 1
    #             st.rerun()
    #     with cols[1]:
    #         if st.button("Próxima", disabled=st.session_state['page_number'] >= total_pages):
    #             st.session_state['page_number'] += 1
    #             st.rerun()
    #     with cols[2]:
    #         st.write(f"Página {st.session_state['page_number']} de {total_pages}")

    #     if noticias:
    #         noticias_data = [noticia.model_dump() for noticia in noticias]
    #         campos = list(noticias_data[0].keys())
    #         campos.extend(["Editar", "Excluir"])

    #         header_cols = st.columns(len(campos))
    #         # for i, campo in enumerate(campos):
    #         #     header_cols[i].write(f"**{campo}**")

    #         for noticia in noticias_data:
    #             col1, col2, col3 = st.columns([1,2,16])

    #             with col1:
    #                 st.markdown(render_minibox('ID', noticia["ID"]), unsafe_allow_html=True)

    #             with col2:
    #                 st.markdown(render_box('Categoria', noticia['CATEGORIA']), unsafe_allow_html=True)
    #                 st.markdown(render_minibox('Publicação', noticia['DATA_PUBLICACAO']), unsafe_allow_html=True)
    #                 st.markdown(render_minibox('Extração', noticia['DT_RASPAGEM']), unsafe_allow_html=True)
    #                 # st.markdown(render_minibox('Decode', noticia['DT_DECODE']), unsafe_allow_html=True)

    #                 st.markdown(render_status('🚧', noticia['STATUS'] ), unsafe_allow_html=True)
    #                 # if st.button("Editar", key=f"edit_{noticia['ID']}_{st.session_state['page_number']}", use_container_width=True):
    #                 #     st.session_state['edit_mode'] = True
    #                 #     st.session_state['edit_id'] = noticia['ID']
    #                 #     st.rerun()
    #                 if st.button("Excluir", key=f"delete_{noticia['ID']}_{st.session_state['page_number']}", use_container_width=True):
    #                     # noticia_service.deletar_noticia(noticia['ID'])
    #                     update_data = NoticiaRaspadaUpdateSchema(STATUS='99-DELETED')
    #                     noticia_service.atualizar_noticia(noticia['ID'], update_data)
    #                     st.success(f"Notícia ID {noticia['ID']} excluída com sucesso.")
    #                     st.rerun()

    #             with col3:
    #                 st.markdown(render_box('Fonte', noticia['FONTE']), unsafe_allow_html=True)
    #                 st.markdown(render_box('Título', noticia['TITULO']), unsafe_allow_html=True)
    #                 st.markdown(f'**Link Google:** [Acessar link]({noticia["LINK_ORIGINAL"]})')

    #                 if noticia['URL'] is None or noticia['STATUS'] == '15-URL-CHK':
    #                     with st.form(key=f"link_form_{noticia['ID']}"):
    #                         link = st.text_input('**Link Notícia**', value='')
    #                         salvar_link = st.form_submit_button("Salvar")
    #                         if salvar_link:
    #                             # Atualizando o registro no banco de dados com o novo URL
    #                             update_data = NoticiaRaspadaUpdateSchema(URL=link, STATUS='10-URL-OK')
    #                             noticia_service.atualizar_noticia(noticia['ID'], update_data)
    #                             st.success(f"URL da notícia ID {noticia['ID']} atualizada com sucesso.")
    #                             st.rerun()
    #                 else:
    #                     st.markdown(f'**Link Notícia:** [{noticia["URL"]}]({noticia["URL"]})')

    #             st.write('---')
    #     else:
    #         st.info("Nenhuma notícia encontrada.")


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


    # Controle de fluxo entre listagem e edição
    if st.session_state['edit_mode'] and st.session_state['edit_id']:
        editar_noticia(st.session_state['edit_id'])
    else:
        listar_noticias()

    # Fechando a sessão do banco de dados
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
