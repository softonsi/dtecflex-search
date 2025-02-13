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
import re

def is_valid_cpf(cpf: str) -> bool:
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11:
        return False
    if cpf == cpf[0] * 11:
        return False
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = 11 - (soma % 11)
    if digito1 >= 10:
        digito1 = 0
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = 11 - (soma % 11)
    if digito2 >= 10:
        digito2 = 0
    return cpf[-2:] == f"{digito1}{digito2}"

def is_valid_cnpj(cnpj: str) -> bool:
    cnpj = re.sub(r'\D', '', cnpj)
    if len(cnpj) != 14:
        return False
    if cnpj == cnpj[0] * 14:
        return False
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
    digito1 = 11 - (soma % 11)
    if digito1 >= 10:
        digito1 = 0
    pesos2 = [6] + pesos1
    soma = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
    digito2 = 11 - (soma % 11)
    if digito2 >= 10:
        digito2 = 0
    return cnpj[-2:] == f"{digito1}{digito2}"

colunas = [
    'APELIDO', 'NOME', 'CPF', 'NOME CPF', 'ATIVIDADE', 'PESSOA', 'SEXO', 'INDICADOR_PPE', 'IDADE',
    'ANIVERSARIO', 'ENVOLVIMENTO', 'OPERACAO',
    'FLG_PESSOA_PUBLICA', 'ENVOLVIMENTO_GOV'
]

def generate_input_widget(coluna, valor, key_prefix, disabled=False):
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
    elif coluna in ['ENVOLVIMENTO_GOV', 'FLG_PESSOA_PUBLICA', 'INDICADOR_PPE']:
        input_value = st.toggle(
            label=coluna,
            value=valor,
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
    return input_value

@require_authentication
def main(current_user=None):
    st.set_page_config(
        page_title="Extração de Nomes",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    # ... (carregamento de CSS e navsidebar)
    from view_components.components.shared.navsidebar import navsidebar  # se necessário
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
        TEXT = noticia.get('TEXTO_NOTICIA')
        if not TEXT and noticia["URL"]:
            from view_components.services.extract_page.page_content_fetcher import PageContentFetcher
            fetcher = PageContentFetcher()
            try:
                extracted_text = fetcher.fetch_and_extract_text(noticia["URL"])
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
    
    st.markdown("### Nomes Salvos")
    if saved_names_list:
        for idx, item in enumerate(saved_names_list):
            is_deleted = False
            expander_label = f"{item.get('NOME', '')}"
            with st.expander(expander_label, expanded=False):
                key_prefix = f"saved_{item['ID']}"
                with st.form(key=f'{key_prefix}form{item["ID"]}'):
                    cols_layout = st.columns([2, 8])
                    input_values = {}
                    with cols_layout[0]:
                        for coluna in colunas:
                            valor = item.get(coluna, '')
                            input_value = generate_input_widget(coluna, valor, key_prefix=key_prefix, disabled=False)
                            input_values[coluna] = input_value

                    col_buttons = st.columns([9, 9, 8])
                    with col_buttons[0]:
                        submitted = st.form_submit_button("Atualizar")
                    with col_buttons[1]:
                        delete_submitted = st.form_submit_button("Deletar")

                    if submitted:
                        valid = True
                        cpf_input = input_values.get('CPF', '')
                        cpf_digits = ''.join(filter(str.isdigit, cpf_input))
                        if len(cpf_digits) == 11:
                            if not is_valid_cpf(cpf_digits):
                                st.error("CPF inválido!")
                                valid = False
                            else:
                                input_values['PESSOA'] = 'PF'
                        elif len(cpf_digits) == 14:
                            if not is_valid_cnpj(cpf_digits):
                                st.error("CNPJ inválido!")
                                valid = False
                            else:
                                input_values['PESSOA'] = 'PJ'
                        else:
                            st.error("CPF/CNPJ deve ter 11 ou 14 dígitos!")
                            valid = False

                        if not input_values.get('NOME'):
                            st.error("O campo NOME é obrigatório!")
                            valid = False

                        if valid:
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

    st.markdown("### Nomes Extraídos")
    if extracted_names_list:
        for idx, item in enumerate(extracted_names_list):
            is_deleted = item.get('deleted', False)
            expander_label = f"{item.get('NOME', '')}"
            if is_deleted:
                expander_label = f"~{expander_label}~ (Excluído)"
            with st.expander(expander_label, expanded=False):
                key_prefix = f"deleted_{item['NOME']}" if is_deleted else f"extracted_{item['NOME']}"
                with st.form(key=f'{key_prefix}form{item["NOME"]}'):
                    cols_layout = st.columns([2, 8])
                    input_values = {}
                    with cols_layout[0]:
                        for coluna in colunas:
                            valor = item.get(coluna, '')
                            input_value = generate_input_widget(coluna, valor, key_prefix=key_prefix, disabled=is_deleted)
                            input_values[coluna] = input_value

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
                        valid = True
                        cpf_input = input_values.get('CPF', '')
                        cpf_digits = ''.join(filter(str.isdigit, cpf_input))
                        if len(cpf_digits) == 11:
                            if not is_valid_cpf(cpf_digits):
                                st.error("CPF inválido!")
                                valid = False
                            else:
                                input_values['PESSOA'] = 'PF'
                        elif len(cpf_digits) == 14:
                            if not is_valid_cnpj(cpf_digits):
                                st.error("CNPJ inválido!")
                                valid = False
                            else:
                                input_values['PESSOA'] = 'PJ'
                        else:
                            st.error("CPF/CNPJ deve ter 11 ou 14 dígitos!")
                            valid = False

                        if not input_values.get('NOME'):
                            st.error("O campo NOME é obrigatório!")
                            valid = False

                        if valid:
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

                    if is_deleted and 'restore_submitted' in locals() and restore_submitted:
                        item['deleted'] = False
                        st.session_state[f'{noticia_id}_is_extracted'][idx] = item
                        st.rerun()

if __name__ == "__main__":
    main()
