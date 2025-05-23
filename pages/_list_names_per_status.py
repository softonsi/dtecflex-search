from datetime import date, datetime
from decimal import Decimal
import hashlib
import uuid
import pandas as pd
import streamlit as st
from backend.resources.notice_name.noticia_nome import NoticiaRaspadaBaseSchema
from backend.resources.notice_name.noticia_nome_service import NoticiaNomeService
from database import SessionLocal
from backend.resources.notice.noticia import (
    NoticiaRaspadaUpdateSchema,
)
from backend.resources.notice.noticia_service import NoticiaService

from view_components.components.home.filters.index import filters
from view_components.components.shared.navsidebar import navsidebar
from view_components.middleware.check_auth import require_authentication
from database import SessionLocal

session = SessionLocal()

noticia_name_service = NoticiaNomeService(session)
noticia_service = NoticiaService(session)

def generate_hash() -> str:
    return hashlib.sha256(uuid.uuid4().bytes).hexdigest()[:16]

def init_page_layout():
    st.set_page_config(page_title="Lista de nomes por status", layout='wide')
    load_css()

def load_css():
    css = """
        <style>
            .stMainBlockContainer{
                padding-top: 2rem;
                padding-bottom: 0rem;
                padding-left: 2rem;
                padding-right: 2rem;
            }
            /* Configuração geral compacta */
            .block-container {
                padding-top: 2.5rem;
                padding-bottom: 0rem;
            }
            .element-container {
                margin-bottom: 0.5rem;
            }
            /* Estilo dos botões em azul pastel */
            .stButton>button {
                background-color: #E1F0FF;
                color: #2C7BE5;
                border: 1px solid #BFD9F9;
                padding: 0.2rem 0.5rem;
                border-radius: 4px;
                transition: all 0.2s;
            }
            .stButton>button:hover {
                background-color: #CAE4FF;
                border-color: #2C7BE5;
            }
            /* Textbox mais compacto */
            .stTextInput input {
                padding: 0.2rem 0.4rem;
                line-height: 1.1;
                font-size: 0.9rem;
            }
            /* Outros ajustes */
            /* ... resto do CSS ... */
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    st.markdown('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">', unsafe_allow_html=True)

session = SessionLocal()
noticia_name_service = NoticiaNomeService(session)

@require_authentication
def main(current_user):
    init_page_layout()

    status = st.query_params.get("status_to_list") or st.session_state.get("status_to_list")
    if status:
        st.session_state["status_to_list"] = status
    else:
        st.info("Use ?status=203-PUBLISHED (por exemplo) na URL ou selecione um status.")
        return

    dados = noticia_name_service.listar_nomes_por_status_e_data_hoje(status)

    if not dados:
        st.warning("Nenhum registro encontrado para o status e data de hoje.")
        return

    for row in dados:
        idade = row.get("IDADE")
        row["IDADE"] = int(idade) if isinstance(idade, Decimal) else idade or 0

        aniversario = row.get("ANIVERSARIO")
        row["ANIVERSARIO"] = aniversario.strftime("%Y-%m-%d") if aniversario else ""

        row["CPF"] = row.get("CPF") or ""

    df = pd.DataFrame(dados)
    df = df.rename(columns={
        "ID": "ID Nome",
        "NOTICIA_ID": "ID Notícia",
        "REG_NOTICIA": "nº de registro",
        "NOME": "Nome",
        "CPF": "CPF",
        "NOME_CPF": "Nome/CPF",
        "APELIDO": "Apelido",
        "OPERACAO": "Operação",
        "SEXO": "Sexo",
        "PESSOA": "Pessoa",
        "IDADE": "Idade",
        "ATIVIDADE": "Atividade",
        "ENVOLVIMENTO": "Envolvimento",
        "TIPO_SUSPEITA": "Tipo Suspeita",
        "FLG_PESSOA_PUBLICA": "Pessoa Pública",
        "ANIVERSARIO": "Aniversário",
        "INDICADOR_PPE": "Indicador PPE",
    })

    label_map = {
        "205-TRANSFERED": "Transferidas",
        "200-TO-APPROVE": "Aguardando aprovação",
        "201-APPROVED": "Aprovadas",
        "203-PUBLISHED": "Publicadas",
    }

    st.markdown(f"### 📋 Nomes de notícias {label_map[status].lower()}")
    st.dataframe(df, use_container_width=True)
if __name__ == "__main__":
    main()
