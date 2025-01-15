from view_components.components.extract_page.notice_info.index import notice_info
from view_components.components.shared.navsidebar import navsidebar
from view_components.middleware.check_auth import require_authentication
from view_components.services.extract_page.page_content_fetcher import PageContentFetcher
from view_components.components.extract_page.text_with_highlighted_names.index import text_with_highlighted_names
from backend.resources.notice.noticia import NoticiaRaspadaUpdateSchema
from backend.resources.notice_name.noticia_nome import NoticiaRaspadaNomeCreateSchema
from backend.resources.notice_name.noticia_nome_service import NoticiaNomeService
from backend.resources.notice.noticia_service import NoticiaService
import streamlit as st
import pandas as pd
from database import SessionLocal

@require_authentication
def main(current_user=None):
    # current_user={'user_id': 5, 'username': 'gabrielfdias2', 'admin': True, 'exp': 1736788749}
    st.set_page_config(
        page_title="Extração de Nomes",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    navsidebar(current_user)
    session = SessionLocal()

    noticia_name_service = NoticiaNomeService(session)
    noticia_service = NoticiaService(session)


    if 'noticia_id' in st.query_params:
        noticia_id = st.query_params['noticia_id']
    else:
        noticia_id = st.session_state.get('id_notice_to_analyze')

    noticia = noticia_service.get_by_id_with_names(noticia_id)

    extracted_names_list = []

    URL = st.text_input('URL', value=noticia['URL'])

    if 'url' not in st.session_state:
        st.session_state['url'] = ''

    if 'id_notice_to_analyze' not in st.session_state:
        st.session_state['id_notice_to_analyze'] = None

    if 'noticia_id' not in st.query_params:
        st.query_params.from_dict({'noticia_id': st.session_state.get('id_notice_to_analyze')})

    if f'{noticia_id}_is_extracted' not in st.session_state:
        st.session_state[f'{noticia_id}_is_extracted'] = []

    if not noticia['ID_USUARIO']:
        update_data = NoticiaRaspadaUpdateSchema(ID_USUARIO=current_user['user_id'], STATUS='07-EDIT-MODE')
        noticia_service.atualizar_noticia(noticia['ID'], update_data)

    if noticia:
        print('NOTICIA:::', noticia['ID'])
        TEXT = noticia.get('TEXTO_NOTICIA')
        if not TEXT and URL:
            fetcher = PageContentFetcher()
            try:
                extracted_text = fetcher.fetch_and_extract_text(URL)
                update_data = NoticiaRaspadaUpdateSchema(TEXTO_NOTICIA=extracted_text)
                noticia_service.atualizar_noticia(noticia['ID'], update_data)
                message = "Notícia atualizada com sucesso!"
                st.toast(message)
            except Exception as e:
                print('erro')
                message = f"Erro ao tentar extrair o conteúdo: {str(e)}"
                st.toast(message)

    notice_info(noticia)

    names_to_highlight, saved_names_list, extracted_names_list = text_with_highlighted_names(noticia['ID'])
    
    colunas = [
        'APELIDO', 'NOME', 'CPF', 'NOME CPF', 'ATIVIDADE', 'PESSOA', 'SEXO', 'INDICADOR_PPE', 'IDADE',
        'ANIVERSARIO', 'ENVOLVIMENTO', 'OPERACAO',
        'FLG_PESSOA_PUBLICA', 'ENVOLVIMENTO_GOV'
    ]

    st.markdown("""
        <style>
        .compact-input .stTextInput > div {
            margin: 0 !important;
            padding: 0 !important;
        }
        .compact-input .stTextInput > div > label {
            font-size: 8px !important;
            margin-bottom: 0px !important;
        }
        .compact-input .stTextInput > div > div {
            padding: 0 !important;
        }
        .compact-input .stTextInput > div > div > input {
            height: 0px !important;
            padding: 2px !important;
        }
        </style>
        """, unsafe_allow_html=True)

    def generate_input_widget(coluna, valor, key_prefix, disabled=False):
        st.markdown('<div class="compact-input">', unsafe_allow_html=True)
        if coluna == 'SEXO':
            input_value = st.selectbox(
                label=coluna,
                options=['M', 'F', 'N/A'],
                index=['M', 'F', 'N/A'].index(valor) if valor in ['M', 'F', 'N/A'] else 2,
                key=f"{key_prefix}_{coluna}",
                disabled=disabled
            )
        elif coluna == 'PESSOA':
            input_value = st.selectbox(
                label=coluna,
                options=['PF', 'PJ', 'NA'],
                index=['PF', 'PJ', 'NA'].index(valor) if valor in ['PF', 'PJ', 'NA'] else 2,
                key=f"{key_prefix}_{coluna}",
                disabled=disabled
            )
        elif coluna == 'IDADE':
            input_value = st.number_input(
                label=coluna,
                value=int(valor) if valor and str(valor).isdigit() else 0,
                min_value=0,
                max_value=199,
                key=f"{key_prefix}_{coluna}",
                disabled=disabled
            )
        elif coluna == 'ANIVERSARIO':
            try:
                date_value = pd.to_datetime(valor).date() if valor else None
            except Exception:
                date_value = None
            input_value = st.date_input(
                label=coluna,
                value=date_value if date_value else None,
                key=f"{key_prefix}_{coluna}",
                disabled=disabled
            )
        elif coluna == 'ENVOLVIMENTO_GOV' or coluna == 'FLG_PESSOA_PUBLICA':
            bool_value = True if str(valor) == 'True' else False
            input_value = st.toggle(
                label=coluna,
                value=bool_value,
                key=f"{key_prefix}_{coluna}",
                disabled=disabled
            )
        elif coluna == 'INDICADOR_PPE':
            input_value = st.toggle(
                label=coluna,
                value=bool(valor) if valor else False,
                key=f"{key_prefix}_{coluna}",
                disabled=disabled
            )
        else:
            input_value = st.text_input(
                label=coluna,
                value=valor if valor is not None else '',
                key=f"{key_prefix}_{coluna}",
                disabled=disabled
            )
        st.markdown('</div>', unsafe_allow_html=True)
        return input_value

    if saved_names_list:
        st.markdown("#### Nomes Salvos")
        for idx, item in enumerate(saved_names_list):
            is_deleted = False
            
            expander_label = f"{item.get('NOME', '')}"

            with st.expander(expander_label, expanded=False):
                key_prefix = f"saved_{item['ID']}"

                with st.form(key=f'{key_prefix}form{item["ID"]}'):
                    
                    st.markdown("""
                        <style>
                            .st-emotion-cache-i6nec9 {
                                gap: 0rem !important;  /* Remove completamente o gap */
                            }
                            div[data-testid="column"] {
                                gap: 0rem !important;  /* Remove completamente o gap entre colunas */
                            }
                            .stTextInput, .stSelectbox, .stDateInput, .stNumberInput {
                                margin-bottom: 5px !important;  /* Reduz o espaçamento entre os inputs */
                            }
                        </style>
                    """, unsafe_allow_html=True)

                    cols_layout = st.columns([2, 8])

                    with cols_layout[0]:
                        input_values = {}
                        for coluna in colunas:
                            valor = item.get(coluna, '')
                            disabled = is_deleted

                            if coluna in ['SEXO', 'PESSOA']:
                                with st.container():
                                    st.markdown('<div class="compact-selectbox">', unsafe_allow_html=True)
                                    input_value = generate_input_widget(coluna, valor, key_prefix=key_prefix, disabled=disabled)
                                    st.markdown('</div>', unsafe_allow_html=True)
                            else:
                                with st.container():
                                    st.markdown('<div class="compact-input">', unsafe_allow_html=True)
                                    input_value = generate_input_widget(coluna, valor, key_prefix=key_prefix, disabled=disabled)
                                    st.markdown('</div>', unsafe_allow_html=True)

                            input_values[coluna] = input_value

                    with cols_layout[0]:
                        col_buttons = st.columns([9, 9, 8])
                        with col_buttons[0]:
                            submitted = st.form_submit_button("Atualizar")
                        with col_buttons[1]:
                            delete_submitted = st.form_submit_button("Deletar")

                    if submitted:
                        data = NoticiaRaspadaNomeCreateSchema(
                            CPF=input_values.get('CPF'),
                            NOME=input_values.get('NOME'),
                            APELIDO=input_values.get('APELIDO'),
                            NOME_CPF=input_values.get('NOME CPF'),
                            SEXO=None if input_values.get('SEXO') == 'N/A' else input_values.get('SEXO'),
                            PESSOA=input_values.get('PESSOA'),
                            IDADE=input_values.get('IDADE'),
                            ANIVERSARIO=input_values.get('ANIVERSARIO'),
                            ATIVIDADE=input_values.get('ATIVIDADE'),
                            ENVOLVIMENTO=input_values.get('ENVOLVIMENTO'),
                            OPERACAO=input_values.get('OPERACAO'),
                            FLG_PESSOA_PUBLICA=input_values.get('FLG_PESSOA_PUBLICA'),
                            ENVOLVIMENTO_GOV=input_values.get('ENVOLVIMENTO_GOV'),
                            INDICADOR_PPE=input_values.get('INDICADOR_PPE'),
                            NOTICIA_ID=noticia_id
                        )
                        noticia_name_service.update(item['ID'], data)
                        st.toast(f"Dados de {input_values.get('NOME')} atualizados com sucesso!")
                        st.rerun()

                    if delete_submitted:
                        sucesso = noticia_name_service.delete(item['ID'])
                        if sucesso:
                            st.toast(f"Dados de {input_values.get('NOME')} deletados com sucesso!")
                            st.rerun()
                        else:
                            st.error(f"Erro ao deletar {item.get('NOME')}")

    if extracted_names_list:
        st.markdown("#### Nomes Extraídos")
        for idx, item in enumerate(extracted_names_list):
            is_deleted = item.get('deleted', False)
            expander_label = f"{item.get('NOME', '')}"
            if is_deleted:
                expander_label = f"~{expander_label}~ (Excluído)"

            with st.expander(expander_label, expanded=False):
                key_prefix = f"deleted_{item['ID']}" if is_deleted else f"extracted_{item['ID']}"

                with st.form(key=f'{key_prefix}form{item["ID"]}'):
                    
                    st.markdown("""
                        <style>
                            .st-emotion-cache-i6nec9 {
                                gap: 0rem !important;  /* Remove completamente o gap */
                            }
                            div[data-testid="column"] {
                                gap: 0rem !important;  /* Remove completamente o gap entre colunas */
                            }
                            .stTextInput, .stSelectbox, .stDateInput, .stNumberInput {
                                margin-bottom: 5px !important;  /* Reduz o espaçamento entre os inputs */
                            }
                        </style>
                    """, unsafe_allow_html=True)

                    cols_layout = st.columns([2, 8])

                    with cols_layout[0]:
                        input_values = {}
                        for coluna in colunas:
                            valor = item.get(coluna, '')
                            disabled = is_deleted

                            if coluna in ['SEXO', 'PESSOA']:
                                with st.container():
                                    st.markdown('<div class="compact-selectbox">', unsafe_allow_html=True)
                                    input_value = generate_input_widget(coluna, valor, key_prefix=key_prefix, disabled=disabled)
                                    st.markdown('</div>', unsafe_allow_html=True)
                            else:
                                with st.container():
                                    st.markdown('<div class="compact-input">', unsafe_allow_html=True)
                                    input_value = generate_input_widget(coluna, valor, key_prefix=key_prefix, disabled=disabled)
                                    st.markdown('</div>', unsafe_allow_html=True)

                            input_values[coluna] = input_value

                    with cols_layout[0]:
                        col_buttons = st.columns([9, 9, 8])
                        with col_buttons[0]:
                            if not is_deleted:
                                submitted = st.form_submit_button("Salvar")
                            else:
                                restore_submitted = st.form_submit_button("Restaurar")
                        with col_buttons[1]:
                            if not is_deleted:
                                delete_submitted = st.form_submit_button("Excluir")


                    if not is_deleted and submitted:
                        data = NoticiaRaspadaNomeCreateSchema(
                            CPF=input_values.get('CPF'),
                            NOME=input_values.get('NOME'),
                            APELIDO=input_values.get('APELIDO'),
                            NOME_CPF=input_values.get('NOME CPF'),
                            SEXO=None if input_values.get('SEXO') == 'N/A' else input_values.get('SEXO'),
                            PESSOA=input_values.get('PESSOA'),
                            IDADE=input_values.get('IDADE'),
                            ANIVERSARIO=input_values.get('ANIVERSARIO'),
                            ATIVIDADE=input_values.get('ATIVIDADE'),
                            # ENVOLVIMENTO=input_values.get('ENVOLVIMENTO'),
                            OPERACAO=input_values.get('OPERACAO'),
                            FLG_PESSOA_PUBLICA=input_values.get('FLG_PESSOA_PUBLICA'),
                            ENVOLVIMENTO_GOV=input_values.get('ENVOLVIMENTO_GOV'),
                            INDICADOR_PPE=input_values.get('INDICADOR_PPE'),
                            NOTICIA_ID=noticia_id
                        )
                        noticia_name_service.create(data)
                        st.toast(f"Dados de {input_values.get('NOME')} salvos com sucesso!")
                        extracted_names_list.pop(idx)
                        st.session_state[f'{noticia_id}_is_extracted'] = extracted_names_list
                        st.rerun()

                    if not is_deleted and delete_submitted:
                        item['deleted'] = True
                        st.session_state[f'{noticia_id}_is_extracted'][idx] = item
                        st.rerun()

                    if is_deleted and restore_submitted:
                        item['deleted'] = False
                        st.session_state[f'{noticia_id}_is_extracted'][idx] = item
                        st.rerun()

if __name__ == "__main__":
    main()