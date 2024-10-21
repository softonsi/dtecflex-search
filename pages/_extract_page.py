from database import SessionLocal
from repositories.noticia_nome_repository import NoticiaNomeRepository
from repositories.noticia_repository import NoticiaRepository
from schemas.noticia import NoticiaRaspadaUpdateSchema
from schemas.noticia_nome import NoticiaRaspadaNomeByNoticiaId, NoticiaRaspadaNomeCreateSchema
from services.noticia_nome_service import NoticiaNomeService
from services.noticia_service import NoticiaService
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os
from datetime import datetime
import re
import emoji
import json

import io

session = SessionLocal()

client = OpenAI()

noticia_name_repository = NoticiaNomeRepository(session)
noticia_name_service = NoticiaNomeService(noticia_name_repository)
noticia_repository = NoticiaRepository(session)
noticia_service = NoticiaService(noticia_repository)

st.set_page_config(
    page_title="Extração de Nomes",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if 'url' not in st.session_state:
    st.session_state['url'] = ''
if 'id_notice_to_analyze' not in st.session_state:
    st.session_state['id_notice_to_analyze'] = None

TEXT = ''
URL = st.session_state['url']
URL = st.text_input('URL', value=URL)
server_fonte = ''

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

noticia_id = st.session_state['id_notice_to_analyze']

if f'{noticia_id}_is_extracted' not in st.session_state:
    st.session_state[f'{noticia_id}_is_extracted'] = {}

noticia_names = []
resposta_dict = {}
names_list = []

if noticia_id:
    noticia_names = noticia_name_service.find_noticia_nome_by_noticia_id(noticia_id)
    if noticia_names and hasattr(noticia_names[0], 'noticia') and noticia_names[0].noticia.TEXTO_NOTICIA:
        TEXT = noticia_names[0].noticia.TEXTO_NOTICIA
        print('Usando texto da notícia salvo no banco de dados')
    else:
        if URL:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(URL, headers=headers)
                if response.status_code == 200:
                    server_fonte = URL.split('/')[2]
                    soup = BeautifulSoup(response.content, 'html.parser')
                    texto = '\n'.join([p.get_text() for p in soup.find_all('p')])
                    TEXT = texto
                    if noticia_names and hasattr(noticia_names[0], 'noticia'):
                        update_data = NoticiaRaspadaUpdateSchema(TEXTO_NOTICIA=TEXT)
                        noticia_service.atualizar_noticia(noticia_names[0].noticia.ID, update_data)
                else:
                    st.error(f"Erro ao acessar a página. Código de status: {response.status_code}")
            except Exception as e:
                st.error(f"Erro ao acessar a URL: {e}")
        else:
            st.error("URL não fornecida para realizar o scraping.")
else:
    if URL:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(URL, headers=headers)
            if response.status_code == 200:
                server_fonte = URL.split('/')[2]
                soup = BeautifulSoup(response.content, 'html.parser')
                texto = '\n'.join([p.get_text() for p in soup.find_all('p')])
                TEXT = texto
            else:
                st.error(f"Erro ao acessar a página. Código de status: {response.status_code}")
        except Exception as e:
            st.error(f"Erro ao acessar a URL: {e}")
    else:
        st.error("ID da notícia não encontrado e URL não fornecida.")

def destaque_nomes(texto, lista_nomes):
    for nome in lista_nomes:
        nome_escapado = re.escape(nome)
        texto = re.sub(r'\b{}\b'.format(nome_escapado),
                       f'<span style="background-color: yellow;">{nome}</span>',
                       texto, flags=re.IGNORECASE)
    return texto.replace('$', '\\$')

if noticia_names:
    names_list = []
    for item in noticia_names:
        item_dict = {
            'NOME': item.NOME,
            'CPF': item.CPF,
            'APELIDO': item.APELIDO,
            'NOME CPF': item.NOME_CPF,
            'SEXO': item.SEXO,
            'PESSOA': item.PESSOA,
            'IDADE': item.IDADE,
            'ANIVERSARIO': item.ANIVERSARIO,
            'ATIVIDADE': item.ATIVIDADE,
            'ENVOLVIMENTO': item.ENVOLVIMENTO,
            # 'OPERACAO': item.OPERACAO,
            'FLG_PESSOA_PUBLICA': item.FLG_PESSOA_PUBLICA,
            # 'INDICADOR_PPE': item.INDICADOR_PPE,
        }
        names_list.append(item_dict)
    print('Usando nomes da notícia salvos no banco de dados')
else:
    if TEXT:
        prompt = """hello world"""
        artigo = f"<artigo>\n{TEXT}\n</artigo>"

        if not st.session_state[f'{noticia_id}_is_extracted']:
            try:
                with st.spinner('Analisando o texto...'):
                    prompt = """Você irá atuar como interpretador avançado de textos e notícias, checagem de fatos. O objetivo principal é localizar nomes de pessoas envolvidadas em crimes ou outras ilicitudes. Cada nome deverá ser listado com outras informações que podem ser obtidas na noticia e conforme as regras abaixo.
                    O texto será fornecido delimitado com a tag "artigo"
                    Localize cada NOME de pessoa ou EMPRESA citada no texto, resumindo seu ENVOLVIMENTO em ilicitos ou crime e conforme contexto, crie uma CLASSIFICACAO como acusado, suspeito, investigado, denunciado, condenado, preso, réu, vítima.
                    Não incluir nomes de vítimas.
                    Nunca omitir o cabeçalho.
                    Não mostrar marcadores de markdown.
                    Mostrar como resultado APENAS um array de json, cada objeto deve conter essas propriedades:
                    ORDEM|NOME|IDADE|ATIVIDADE|CLASSIFICACAO|ENVOLVIMENTO|OPERACAO
                    caso você não extraia certa informação de uma respectiva pessoa retorna como null mesmo, por exemplo:
                        {
                            ENVOLVIMENTO: null
                        }
                    """
                    response = client.chat.completions.create(
                        model='gpt-4o-mini',
                        messages=[
                            {"role": "system", "content": prompt},
                            {"role": "user", "content": artigo}
                        ]
                    )

                resposta = response.choices[0].message.content

                resposta_dict = json.loads(resposta)

                st.session_state[f'{noticia_id}_is_extracted'] = resposta_dict

            except Exception as e:
                print('error', e)
                st.error(f"Erro ao processar a chamada à API: {e}")

        names_list = st.session_state[f'{noticia_id}_is_extracted']

names_to_highlight = [item['NOME'] for item in names_list if 'NOME' in item]

with st.expander('Texto notícia e nomes destacados', expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div style="font-size:14px; white-space: pre-wrap;">{}</div>'.format(TEXT), unsafe_allow_html=True)
    with col2:
        if TEXT and names_to_highlight:
            highlighted_text = destaque_nomes(TEXT, names_to_highlight)
            st.markdown('<div style="font-size:14px; white-space: pre-wrap;">{}</div>'.format(highlighted_text), unsafe_allow_html=True)
        else:
            st.write("Nenhum nome para destacar.")

colunas = [
    'NOME', 'CPF', 'APELIDO', 'NOME CPF', 'SEXO', 'PESSOA', 'IDADE',
    'ANIVERSARIO', 'ATIVIDADE', 'ENVOLVIMENTO', 'OPERACAO',
    'FLG_PESSOA_PUBLICA', 'INDICADOR_PPE'
]

selecionados = names_list

num_columns = 4

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

for idx, item in enumerate(selecionados):
    with st.expander(f"Dados de {item.get('NOME', '')}", expanded=True):
        with st.form(key=f'form_{idx}'):
            input_values = {}
            cols_form = st.columns(num_columns, gap="small")
            for i, coluna in enumerate(colunas):
                valor = item.get(coluna, '')
                with cols_form[i % num_columns]:
                    st.markdown('<div class="compact-input">', unsafe_allow_html=True)
                    input_value = st.text_input(
                        label=coluna,
                        value=valor if valor is not None else '',
                        key=f"{coluna}_{idx}"
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                    input_values[coluna] = input_value
            submitted = st.form_submit_button("Salvar")
            if submitted:
                data = NoticiaRaspadaNomeCreateSchema(
                    CPF=input_values.get('CPF'),
                    NOME=input_values.get('NOME'),
                    APELIDO=input_values.get('APELIDO'),
                    ENVOLVIMENTO=input_values.get('ENVOLVIMENTO'),
                    NOME_CPF=input_values.get('NOME CPF'),
                    OPERACAO=input_values.get('OPERACAO'),
                    ATIVIDADE=input_values.get('ATIVIDADE'),
                    NOTICIA_ID=noticia_id
                )
                noticia_name_service.create(data)
                st.success(f"Dados de {input_values.get('NOME')} salvos com sucesso!")

def msg_confirma(msg):
    st.toast(msg, icon="✅")

cols = st.columns([1, 1, 1, 6, 1, 1])
with cols[0]:
    if st.button('Descartar', use_container_width=True):
        msg_confirma('Notícia descartada')
with cols[2]:
    if st.button('Finalizar', use_container_width=True):
        msg_confirma('Notícia Finalizada')
with cols[5]:
    if st.button('Sair', use_container_width=True):
        msg_confirma('Notícia Finalizada')
