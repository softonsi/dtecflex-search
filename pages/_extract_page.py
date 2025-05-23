import re
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st

from view_components.components.extract_page.notice_info.index import notice_info
from view_components.components.shared.navsidebar import navsidebar
from view_components.middleware.check_auth import require_authentication
from view_components.services.extract_page.page_content_fetcher import PageContentFetcher
from view_components.components.extract_page.text_with_highlighted_names.index import text_with_highlighted_names
from backend.resources.notice.noticia import NoticiaRaspadaUpdateSchema
from backend.resources.notice_name.noticia_nome import NoticiaRaspadaNomeCreateSchema
from backend.resources.notice_name.noticia_nome_service import NoticiaNomeService
from backend.resources.notice.noticia_service import NoticiaService
from database import SessionLocal


def validate_cpf_cnpj(value: str) -> bool:
    value = re.sub(r'\D', '', value)
    if len(value) == 11:
        return validate_cpf(value)
    elif len(value) == 14:
        return validate_cnpj(value)
    return False


def validate_cpf(cpf: str) -> bool:
    if not cpf or len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calculate_digit(digits, weights):
        sum_digits = sum(int(d) * w for d, w in zip(digits, weights))
        remainder = (sum_digits * 10) % 11
        return 0 if remainder == 10 else remainder

    if calculate_digit(cpf[:9], range(10, 1, -1)) != int(cpf[9]):
        return False
    if calculate_digit(cpf[:10], range(11, 1, -1)) != int(cpf[10]):
        return False
    return True


def validate_cnpj(cnpj: str) -> bool:
    if not cnpj or len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    def calculate_digit(digits, weights):
        sum_digits = sum(int(d) * w for d, w in zip(digits, weights))
        remainder = sum_digits % 11
        return 0 if remainder < 2 else 11 - remainder

    if calculate_digit(cnpj[:12], [5,4,3,2,9,8,7,6,5,4,3,2]) != int(cnpj[12]):
        return False
    if calculate_digit(cnpj[:13], [6,5,4,3,2,9,8,7,6,5,4,3,2]) != int(cnpj[13]):
        return False
    return True

def limpar_cpf(cpf: str) -> str:
    return ''.join(ch for ch in cpf if ch.isdigit())

def load_css():
    css = """
        <style>
            .stMainBlockContainer{
                padding-top: 2rem;
                padding-bottom: 0rem;
                padding-left: 2rem;
                padding-right: 2rem;
            }
            .block-container {
                padding-top: 2.5rem;
                padding-bottom: 0rem;
            }
            .element-container {
                margin-bottom: 0.5rem;
            }
            .stButton button {
                background-color: #E1F0FF;
                color: #2C7BE5;
                border: 1px solid #BFD9F9;
                padding: 0.2rem 0.5rem;
                border-radius: 4px;
                transition: all 0.2s;
            }
            .stButton button:hover {
                background-color: #CAE4FF;
                border-color: #2C7BE5;
            }
            .stTextInput input {
                padding: 0.2rem 0.4rem;
                line-height: 1.2;
                font-size: 0.9rem;
            }
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def validate_name_fields(cpf: str, nome_cpf: str, pessoa_tipo: str) -> (bool, str):
    cpf = cpf.strip()
    nome_cpf = nome_cpf.strip()
    pessoa_tipo = pessoa_tipo.strip()
    if (cpf or nome_cpf) and (not cpf or not nome_cpf):
        return False, "Se o CPF/CNPJ estiver preenchido, o campo NOME_CPF também deve estar preenchido."
    if pessoa_tipo in ["NA", "N/A"] and cpf:
        return False, "Se a PESSOA for 'NA', o CPF/CNPJ deve estar vazio."
    if pessoa_tipo in ["PF", "PJ"] and cpf:
        if not validate_cpf_cnpj(cpf):
            return False, "CPF/CNPJ inválido! Verifique os dados antes de salvar."
    return True, ""

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
        session_key = f"{key_prefix}_{coluna}"
        # se já existe no session_state, usa esse valor; senão usa o valor passado (ou 0)
        default_age = (
            st.session_state[session_key]
            if session_key in st.session_state
            else (int(valor) if valor and str(valor).isdigit() else 0)
        )
        input_value = st.number_input(
            label=coluna,
            value=default_age,
            min_value=0,
            max_value=199,
            key=session_key,
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
    elif coluna in ['FLG_PESSOA_PUBLICA', 'INDICADOR_PPE']:
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

# def generate_input_widget(coluna, valor, key_prefix, disabled=False):
#     if coluna == 'SEXO':
#         return st.selectbox(
#             label=coluna,
#             options=['M', 'F', 'N/A'],
#             index=['M','F','N/A'].index(valor) if valor in ['M','F','N/A'] else 2,
#             key=f"{key_prefix}_{coluna}",
#             disabled=disabled
#         )
#     elif coluna == 'PESSOA':
#         return st.selectbox(
#             label=coluna,
#             options=['PF','PJ','NA'],
#             index=['PF','PJ','NA'].index(valor) if valor in ['PF','PJ','NA'] else 2,
#             key=f"{key_prefix}_{coluna}",
#             disabled=disabled
#         )
#     elif coluna == 'IDADE':
#         return st.number_input(
#             label=coluna,
#             value=int(valor) if valor and str(valor).isdigit() else 0,
#             min_value=0, max_value=199,
#             key=f"{key_prefix}_{coluna}",
#             disabled=disabled
#         )
#     elif coluna == 'ANIVERSARIO':
#         try:
#             date_value = pd.to_datetime(valor).date() if valor else None
#         except Exception:
#             date_value = None
#         return st.date_input(
#             label=coluna,
#             value=date_value,
#             key=f"{key_prefix}_{coluna}",
#             disabled=disabled
#         )
#     elif coluna in ['FLG_PESSOA_PUBLICA','INDICADOR_PPE']:
#         return st.toggle(
#             label=coluna,
#             value=valor,
#             key=f"{key_prefix}_{coluna}",
#             disabled=disabled
#         )
#     else:
#         return st.text_input(
#             label=coluna,
#             value=valor or '',
#             key=f"{key_prefix}_{coluna}",
#             disabled=disabled
#         )

@st.cache_data(show_spinner=False)
def buscar_no_dtec(nome: str, rows: int = 20) -> list[dict]:
    # nome_q = quote_plus(nome.strip())
    body = f"""<?xml version="1.0" encoding="UTF-8"?>
<consulta>
  <cliente>2013060601</cliente>
  <usuario>softonTeste</usuario>
  <senha>xuroborus</senha>
  <qry>nome:{nome}</qry>
  <options>rows:{rows}</options>
</consulta>"""
    try:
        resp = requests.post(
            "https://dtec-flex.com.br/dtecflexWS/rest/x/search",
            data=body,
            headers={"Content-Type":"application/xml"},
            timeout=10
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        st.error(f"Erro na requisição DTEC: {e}")
        return []
    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as e:
        st.error(f"Erro ao parsear XML: {e}")
        return []

    results = []
    for doc in root.findall(".//resultList/doc"):
        item = {
            attr.findtext("name"): attr.findtext("value") or ""
            for attr in doc.findall("attribute")
        }
        results.append(item)
    return results

@st.dialog("Resultado da Busca", width="large")
def search_name_dialog(key_prefix: str, nome: str):
    try:
        registros = buscar_no_dtec(nome, rows=20)
    except Exception as e:
        st.error(f"Erro na busca: {e}")
        return

    if not registros:
        st.info("Nenhum registro encontrado.")
        return

    # Só precisamos exibir nome e cpf na tabela
    display_keys = ["nome_exato", "cpf"]
    headers = ["Nome", "CPF", "Ação"]
    cols = st.columns([4, 2, 1])
    for c, h in zip(cols, headers):
        c.markdown(f"**{h}**")

    for idx, reg in enumerate(registros):
        row_cols = st.columns([4, 2, 1])
        row_cols[0].write(reg.get("nome_exato", "–"))
        row_cols[1].write(reg.get("cpf", "–"))

        if row_cols[2].button("Selecionar", key=f"{key_prefix}_res_{idx}"):
            cpf_val = reg.get("cpf", "")
            nome_val = reg.get("nome_exato", "")
            idade_val = reg.get("idade", "")

            # preenche CPF
            st.session_state[f"{key_prefix}_CPF"] = cpf_val
            # preenche NOME_CPF (campo onde se digita o nome vinculado ao CPF)
            st.session_state[f"{key_prefix}_NOME_CPF"] = nome_val
            # se vier idade, converte para int e preenche
            if idade_val:
                try:
                    st.session_state[f"{key_prefix}_IDADE"] = int(idade_val)
                except ValueError:
                    # se não for numérico, apenas ignora ou deixa em branco
                    st.session_state[f"{key_prefix}_IDADE"] = 0

            st.toast(f"Preenchido: CPF={cpf_val}, Nome={nome_val}, Idade={idade_val}")
            st.rerun()

@require_authentication
def main(current_user=None):
    st.set_page_config(
        page_title="Extração de Nomes",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    load_css()
    navsidebar(current_user)
    session = SessionLocal()

    noticia_service = NoticiaService(session)
    noticia_name_service = NoticiaNomeService(session)

    if 'noticia_id' in st.query_params:
        noticia_id = st.query_params['noticia_id']
    else:
        noticia_id = st.session_state.get('id_notice_to_analyze')

    noticia = noticia_service.get_by_id_with_names(noticia_id)
    extracted_names_list = []

    st.session_state.setdefault('url', '')
    st.session_state.setdefault('id_notice_to_analyze', None)
    if 'noticia_id' not in st.query_params:
        st.query_params.from_dict({'noticia_id': st.session_state['id_notice_to_analyze']} )
    st.session_state.setdefault(f'{noticia_id}_is_extracted', [])
    st.session_state.setdefault('show_add_expander', False)

    if noticia and not noticia['ID_USUARIO']:
        try:
            upd = NoticiaRaspadaUpdateSchema(
                ID_USUARIO=current_user['user_id'],
                STATUS='07-EDIT-MODE'
            )
            noticia_service.atualizar_noticia(noticia['ID'], upd)
        except Exception:
            st.error('Erro ao atualizar a notícia')
        finally:
            session.close()

    if noticia:
        TEXT = noticia.get('TEXTO_NOTICIA')
        if not TEXT and noticia.get("URL"):
            fetcher = PageContentFetcher()
            try:
                ext = fetcher.fetch_and_extract_text(noticia["URL"])
                upd = NoticiaRaspadaUpdateSchema(TEXTO_NOTICIA=ext)
                noticia_service.atualizar_noticia(noticia['ID'], upd)
                st.toast("Notícia atualizada com sucesso!")
            except Exception as e:
                st.toast(f"Erro ao extrair conteúdo: {e}")
            finally:
                session.close()

    notice_info(noticia)
    names_to_highlight, saved_names_list, extracted_names_list = text_with_highlighted_names(noticia['ID'])


    colunas = [
        'APELIDO','NOME','CPF','NOME_CPF','ATIVIDADE','PESSOA','SEXO','IDADE',
        'ANIVERSARIO','ENVOLVIMENTO','OPERACAO','FLG_PESSOA_PUBLICA','INDICADOR_PPE'
    ]

    if 'show_add_expander' not in st.session_state:
        st.session_state['show_add_expander'] = False

    if not st.session_state['show_add_expander']:
        if st.button("Adicionar nome", icon=":material/note_add:"):
            st.session_state['show_add_expander'] = True

    if st.session_state['show_add_expander']:
        with st.expander("Adicionar novo nome", expanded=True):
            col_search, _ = st.columns([1,9])
            with col_search:
                if st.button("🔍 Buscar Nome", key="new_buscar", use_container_width=True):
                    nome_para_buscar = st.session_state.get("new_NOME", "")
                    search_name_dialog(key_prefix="new", nome=nome_para_buscar)

            new_values = {}
            new_key_prefix = "new"
            for i in range(0, len(colunas), 3):
                row = colunas[i:i+3]
                cols_form = st.columns(3)
                for j, coluna in enumerate(row):
                    widget_key = f"{new_key_prefix}_{coluna}"
                    default_val = None if widget_key in st.session_state else ""
                    with cols_form[j]:
                        new_values[coluna] = generate_input_widget(
                            coluna, default_val, new_key_prefix, disabled=False
                        )

            btn_cols = st.columns([1,1])
            with btn_cols[0]:
                if st.button("💾 Salvar", key="save_new_name"):
                    cpf = new_values.get('CPF','')
                    nome_cpf = new_values.get('NOME_CPF','')
                    pessoa_tipo = new_values.get('PESSOA','NA')
                    valid, err = validate_name_fields(cpf, nome_cpf, pessoa_tipo)
                    if not valid:
                        st.error(err)
                    else:
                        data = NoticiaRaspadaNomeCreateSchema(
                            CPF=limpar_cpf(cpf),
                            NOME=new_values.get('NOME'),
                            APELIDO=new_values.get('APELIDO'),
                            NOME_CPF=nome_cpf,
                            SEXO=None if new_values.get('SEXO') in (None,'N/A') else new_values.get('SEXO'),
                            PESSOA=pessoa_tipo,
                            IDADE=new_values.get('IDADE'),
                            ANIVERSARIO=new_values.get('ANIVERSARIO'),
                            ATIVIDADE=new_values.get('ATIVIDADE'),
                            ENVOLVIMENTO=new_values.get('ENVOLVIMENTO'),
                            OPERACAO=new_values.get('OPERACAO'),
                            FLG_PESSOA_PUBLICA=new_values.get('FLG_PESSOA_PUBLICA'),
                            INDICADOR_PPE=new_values.get('INDICADOR_PPE'),
                            NOTICIA_ID=noticia['ID']
                        )
                        noticia_name_service.create(data)
                        st.toast(f"Dados de {new_values.get('NOME')} salvos com sucesso!")
                        st.session_state['show_add_expander'] = False
                        st.rerun()
            with btn_cols[1]:
                if st.button("❌ Cancelar", key="cancel_new_name"):
                    st.session_state['show_add_expander'] = False
                    st.rerun()


    
    st.markdown("#### Nomes Salvos")
    for idx, item in enumerate(saved_names_list):
        label = item.get('NOME','')
        with st.expander(label, expanded=False):
            key_prefix = f"saved_{item.get('ID', idx)}"
            with st.form(key=f'{key_prefix}_form'):
                input_vals = {}
                for i in range(0, len(colunas), 3):
                    row = colunas[i:i+3]
                    cols_f = st.columns(3)
                    for j, coluna in enumerate(row):
                        with cols_f[j]:
                            valor = item.get(coluna, '')
                            input_vals[coluna] = generate_input_widget(coluna, valor, key_prefix)
                btns = st.columns(3)
                with btns[0]:
                    submitted = st.form_submit_button("Atualizar")
                with btns[1]:
                    delete_sub = st.form_submit_button("Deletar")
                if submitted:
                    cpf = input_vals.get('CPF','')
                    nome_cpf = input_vals.get('NOME CPF','')
                    pessoa_tipo = input_vals.get('PESSOA','NA')
                    valid, err = validate_name_fields(cpf, nome_cpf, pessoa_tipo)
                    if not valid:
                        st.error(err)
                    else:
                        data = NoticiaRaspadaNomeCreateSchema(
                            CPF=cpf,
                            NOME=input_vals.get('NOME'),
                            APELIDO=input_vals.get('APELIDO'),
                            NOME_CPF=nome_cpf,
                            SEXO=None if input_vals.get('SEXO')=='N/A' else input_vals.get('SEXO'),
                            PESSOA=pessoa_tipo,
                            IDADE=input_vals.get('IDADE'),
                            ANIVERSARIO=input_vals.get('ANIVERSARIO'),
                            ATIVIDADE=input_vals.get('ATIVIDADE'),
                            ENVOLVIMENTO=input_vals.get('ENVOLVIMENTO'),
                            OPERACAO=input_vals.get('OPERACAO'),
                            FLG_PESSOA_PUBLICA=input_vals.get('FLG_PESSOA_PUBLICA'),
                            INDICADOR_PPE=input_vals.get('INDICADOR_PPE'),
                            NOTICIA_ID=noticia['ID']
                        )
                        if 'ID' in item:
                            noticia_name_service.update(item['ID'], data)
                        else:
                            noticia_name_service.create(data)
                        st.toast(f"Dados de {input_vals.get('NOME')} atualizados com sucesso!")
                        st.rerun()
                if delete_sub and 'ID' in item:
                    ok = noticia_name_service.delete(item['ID'])
                    if ok:
                        st.toast(f"Dados de {item.get('NOME')} deletados com sucesso!")
                        st.rerun()
                    else:
                        st.error(f"Erro ao deletar {item.get('NOME')}")

    for idx, item in enumerate(extracted_names_list):
        st.markdown("#### Nomes Extraídos")

        is_deleted = item.get('deleted', False)
        label = item.get('NOME','')
        if is_deleted:
            label = f"~{label}~ (Excluído)"
        with st.expander(label, expanded=False):
            key_prefix = (f"deleted" if is_deleted else "extracted") + f"_{item.get('NOME', idx)}"
            col_search, _ = st.columns([1,9])
            with col_search:
                if st.button("🔍 Buscar Nome", key=f"{key_prefix}_buscar_top", use_container_width=True):
                    search_name_dialog(key_prefix=key_prefix, nome=item.get("NOME",""))
            with st.form(key=f"{key_prefix}_form"):
                input_vals = {}
                for i in range(0, len(colunas), 3):
                    row = colunas[i:i+3]
                    cols_f = st.columns(3)
                    for j, coluna in enumerate(row):
                        with cols_f[j]:
                            valor = item.get(coluna, '')
                            input_vals[coluna] = generate_input_widget(coluna, valor, key_prefix)
                btns2 = st.columns([1,1])
                with btns2[0]:
                    if not is_deleted:
                        submitted = st.form_submit_button("💾 Salvar", use_container_width=True)
                    else:
                        restore_sub = st.form_submit_button("🔄 Restaurar", use_container_width=True)
                with btns2[1]:
                    if not is_deleted:
                        delete_sub = st.form_submit_button("🗑 Excluir", use_container_width=True)
                if not is_deleted and submitted:
                    cpf = input_vals.get('CPF','')
                    nome_cpf = input_vals.get('NOME_CPF','')
                    pessoa_tipo = input_vals.get('PESSOA','NA')

                    valid, err = validate_name_fields(cpf, nome_cpf, pessoa_tipo)
                    if not valid:
                        st.error(err)
                    else:
                        data = NoticiaRaspadaNomeCreateSchema(
                            CPF=limpar_cpf(cpf),
                            NOME=input_vals.get('NOME'),
                            APELIDO=input_vals.get('APELIDO'),
                            NOME_CPF=nome_cpf,
                            SEXO=None if input_vals.get('SEXO') == 'N/A' else input_vals.get('SEXO'),
                            PESSOA=pessoa_tipo,
                            IDADE=input_vals.get('IDADE'),
                            ANIVERSARIO=input_vals.get('ANIVERSARIO'),
                            ATIVIDADE=input_vals.get('ATIVIDADE'),
                            ENVOLVIMENTO=input_vals.get('ENVOLVIMENTO'),
                            OPERACAO=input_vals.get('OPERACAO'),
                            FLG_PESSOA_PUBLICA=input_vals.get('FLG_PESSOA_PUBLICA'),
                            INDICADOR_PPE=input_vals.get('INDICADOR_PPE'),
                            NOTICIA_ID=noticia['ID']
                        )
                        if 'ID' in item:
                            noticia_name_service.update(item['ID'], data)
                        else:
                            noticia_name_service.create(data)

                        st.toast(f"Dados de {input_vals.get('NOME')} salvos com sucesso!")
                        if is_deleted:
                            item['deleted'] = False
                        st.session_state[f"{noticia['ID']}_is_extracted"] = extracted_names_list
                        st.rerun()

                if not is_deleted and delete_sub:
                    ok = noticia_name_service.delete(item['ID'])
                    if ok:
                        st.toast(f"Dados de {item.get('NOME')} excluídos com sucesso!")
                        extracted_names_list.pop(idx)
                        st.session_state[f"{noticia['ID']}_is_extracted"] = extracted_names_list
                        st.rerun()
                    else:
                        st.error(f"Erro ao excluir {item.get('NOME')}")

                if is_deleted and restore_sub:
                    item['deleted'] = False
                    st.session_state[f"{noticia['ID']}_is_extracted"][idx] = item
                    st.rerun()

if __name__ == "__main__":
    main()
