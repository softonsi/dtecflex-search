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
import itertools
import io
from playwright.sync_api import sync_playwright
import time

session = SessionLocal()
client = OpenAI()

noticia_name_repository = NoticiaNomeRepository(session)
noticia_name_service = NoticiaNomeService(noticia_name_repository)
noticia_repository = NoticiaRepository(session)
noticia_service = NoticiaService(noticia_repository)

def init_page_layout():
    st.set_page_config(
        page_title="Extração de Nomes",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown("""
        <style>
            # /* Remove blank space at top and bottom */
            # .block-container {
            #     padding-top: 0rem;
            #     padding-bottom: 0rem;
            # }
            /* Remove blank space at the center canvas */
            .st-emotion-cache-z5fcl4 {
                position: relative;
                top: -62px;
                }
            /* Make the toolbar transparent and the content below it clickable */
            .st-emotion-cache-18ni7ap {
                pointer-events: none;
                background: rgb(255 255 255 / 0%)
                }
            .st-emotion-cache-zq5wmm {
                pointer-events: auto;
                background: rgb(255 255 255);
                border-radius: 5px;
                }
            #MainMenu {visibility: hidden;}

        </style>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auUHMUAnbYt6LPbKhT1Q1u1AL3LlmjMss0bGgi" crossorigin="anonymous">
        """, unsafe_allow_html=True)


def get_page_content(URL: str) -> str:
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'}
    page_content = ''
    try:
        response = requests.get(URL, headers=headers)
        if response.status_code == 2001:
            server_fonte = URL.split('/')[2]
            page_content = response.content
        else:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(URL)
                page.wait_for_load_state(state='networkidle')
                page_content = page.content()
                print(f"URL processada: {page.url}")
                browser.close()

    except Exception as e:
        st.error(f"Erro ao acessar a URL: {e}")

    return page_content

init_page_layout()

if 'url' not in st.session_state:
    st.session_state['url'] = ''
if 'id_notice_to_analyze' not in st.session_state:
    st.session_state['id_notice_to_analyze'] = None

if 'noticia_id' not in st.query_params:
    print('AAAAAAAAAAAAAAAAAAAAAAAa')
    st.query_params.from_dict({'noticia_id': st.session_state.get('id_notice_to_analyze')})

noticia_id = st.query_params['noticia_id']

noticia = noticia_service.get_by_id_with_names(noticia_id)


TEXT = ''
URL = noticia.URL
URL = st.text_input('URL', value=URL)
server_fonte = ''

cols_top = st.columns(3)

if f'{noticia_id}_is_extracted' not in st.session_state:
    st.session_state[f'{noticia_id}_is_extracted'] = []

saved_names_list = []
extracted_names_list = []

if noticia:
    TEXT = noticia.TEXTO_NOTICIA
    if not TEXT and URL:
        page_content = get_page_content(URL)
        soup = BeautifulSoup(page_content, 'html.parser')
        texto = '\n'.join([p.get_text() for p in soup.find_all('p')])
        TEXT = texto
        update_data = NoticiaRaspadaUpdateSchema(TEXTO_NOTICIA=TEXT)
        noticia_service.atualizar_noticia(noticia.ID, update_data)

with cols_top[0]:
    fonte = st.text_input('Fonte', value=noticia.FONTE if noticia and noticia.FONTE else '')
with cols_top[1]:
    titulo = st.text_input('Título', value=noticia.TITULO if noticia and noticia.TITULO else '')
with cols_top[2]:
    categoria = st.text_input('Categoria', value=noticia.CATEGORIA if noticia and noticia.CATEGORIA else '')

cols_bottom = st.columns(3)

with cols_bottom[0]:
    regiao = st.text_input('Região', value=noticia.REGIAO if noticia and hasattr(noticia, 'REGIAO') and noticia.REGIAO else '')
with cols_bottom[1]:
    uf = st.text_input('UF', value=noticia.UF if noticia and hasattr(noticia, 'UF') and noticia.UF else '')

def destaque_nomes(texto, lista_nomes):
    if not isinstance(texto, str):
        texto = '' if texto is None else str(texto)
    
    lt_colors = [
        "LightSkyBlue", "LightCoral", "PaleGreen", "Khaki", 
        "Lavender", "PeachPuff", "MistyRose", "PowderBlue", 
        "Thistle", "PaleTurquoise", "LightSalmon", "Aquamarine"
    ]
    
    dk_colors = [
        "MidnightBlue", "DarkRed", "ForestGreen", "SaddleBrown", 
        "Indigo", "FireBrick", "DarkSlateGray", "DarkOliveGreen", 
        "DarkMagenta", "DarkCyan", "Chocolate", "DarkGoldenrod"
    ]
    
    color_sequence = itertools.cycle(lt_colors)
    
    for nome in lista_nomes:
        if not isinstance(nome, str) or not nome.strip():
            st.warning(f"Nome inválido encontrado: {nome}")
            continue
        texto = texto.replace(
            nome, 
            f'<span style="background-color: {next(color_sequence)}; text-transform: uppercase; font-weight: bold;">{nome}</span>'
        )
    
    texto = texto.replace('\n', '<br>').replace('\r', '<br>')
    
    return texto

if noticia and noticia.nomes_raspados:
    for item in noticia.nomes_raspados:
        item_dict = {
            'ID': item.ID,
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
            # 'FLG_PESSOA_PUBLICA': item.FLG_PESSOA_PUBLICA,
        }
        saved_names_list.append(item_dict)

if TEXT:
    if not st.session_state[f'{noticia_id}_is_extracted']:
        try:
            with st.spinner('Analisando o texto...'):
                prompt = """Você irá atuar como interpretador avançado de textos, notícias e checagem de fatos. O objetivo principal é localizar nomes de pessoas envolvidas em crimes ou outras ilicitudes. Cada nome deverá ser listado com outras informações que podem ser obtidas na notícia e conforme as regras abaixo.
                O texto será fornecido delimitado com a tag "artigo"
                Localize cada NOME, ENTIDADE ou EMPRESA citada no texto, resumindo seu ENVOLVIMENTO em ilícitos ou crime e conforme contexto, crie uma CLASSIFICACAO como acusado, suspeito, investigado, denunciado, condenado, preso, réu, vítima.
                Não incluir nomes de vítimas.
                Não mostrar marcadores de markdown.
                Mostrar como resultado APENAS um array de json. Cada objeto deve conter todas as seguintes propriedades:
                    'NOME', 'CPF', 'APELIDO', 'NOME CPF', 'SEXO' (o valor dessa propriedade caso seja homem será 'M', mulher 'F' e não especificado 'N/A'
                    , 'PESSOA', 'IDADE', 'ANIVERSARIO', 'ATIVIDADE', 'ENVOLVIMENTO', 'OPERACAO', 'FLG_PESSOA_PUBLICA', 'INDICADOR_PPE'
                caso você não encontre certa propriedade de uma pessoa, retorne como null
                """
                artigo = f"<artigo>\n{TEXT}\n</artigo>"
                response = client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": artigo}
                    ]
                )

            resposta = response.choices[0].message.content

            resposta_dict = json.loads(resposta)
            if isinstance(resposta_dict, list):
                for item in resposta_dict:
                    item['deleted'] = False

            st.session_state[f'{noticia_id}_is_extracted'] = resposta_dict

        except Exception as e:
            print('error', e)
            st.error(f"Erro ao processar a chamada à API: {e}")

    extracted_names_list = st.session_state[f'{noticia_id}_is_extracted']

    saved_names_set = set([item['NOME'] for item in saved_names_list if 'NOME' in item])
    extracted_names_list = [item for item in extracted_names_list if item.get('NOME') not in saved_names_set]

names_to_highlight = [
    item['NOME'] 
    for item in saved_names_list + extracted_names_list 
    if 'NOME' in item and isinstance(item['NOME'], str) and item['NOME'].strip()
]

with st.expander('Texto notícia e nomes destacados', expanded=True):
    if TEXT and names_to_highlight:
        highlighted_text = destaque_nomes(TEXT, names_to_highlight)
        st.markdown('<div style="font-size:14px; white-space: pre-wrap;">{}</div>'.format(highlighted_text), unsafe_allow_html=True)
    else:
        st.write("Nenhum nome para destacar ou texto não disponível.")

    @st.dialog(f"Edite o texto da notícia de id {noticia.ID}", width="large")
    def render_area():
        st.markdown(
            """
            <style>
            .big-text-area .stTextArea textarea {
                width: 100% !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        with st.container():
            st.write("Edite o texto da notícia")
            with st.container():
                texto_noticia = st.text_area("Texto da Notícia", value=noticia.TEXTO_NOTICIA, height=300)
                if st.button("Atualizar"):
                    update_data = NoticiaRaspadaUpdateSchema(TEXTO_NOTICIA=texto_noticia)
                    try:
                        noticia_service.atualizar_noticia(noticia.ID, update_data)
                        st.success("Notícia atualizada com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao atualizar a notícia: {e}")

    if "closed_modal" not in st.session_state:
        if st.button("Editar texto"):
            render_area()

colunas = [
    'NOME', 'CPF', 'APELIDO', 'NOME CPF', 'SEXO', 'PESSOA', 'IDADE',
    'ANIVERSARIO', 'ATIVIDADE', 'ENVOLVIMENTO', 'OPERACAO',
    'FLG_PESSOA_PUBLICA', 'INDICADOR_PPE'
]

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

if saved_names_list:
    st.markdown("#### Nomes Salvos")
    for idx, item in enumerate(saved_names_list):
        with st.expander(f"{item.get('NOME', '')}", expanded=False):
            with st.form(key=f'saved_form_{idx}'):
                input_values = {}
                cols_form = st.columns(num_columns, gap="small")
                for i, coluna in enumerate(colunas):
                    valor = item.get(coluna, '')
                    with cols_form[i % num_columns]:
                        st.markdown('<div class="compact-input">', unsafe_allow_html=True)
                        input_value = st.text_input(
                            label=coluna,
                            value=valor if valor is not None else '',
                            key=f"saved_{coluna}_{idx}"
                        )
                        st.markdown('</div>', unsafe_allow_html=True)
                        input_values[coluna] = input_value

                col_buttons = st.columns([1, 1])
                with col_buttons[0]:
                    submitted = st.form_submit_button("Atualizar")
                with col_buttons[1]:
                    delete_submitted = st.form_submit_button("Deletar")

                if submitted:
                    data = NoticiaRaspadaNomeCreateSchema(
                        CPF=input_values.get('CPF'),
                        NOME=input_values.get('NOME'),
                        APELIDO=input_values.get('APELIDO'),
                        ENVOLVIMENTO=input_values.get('ENVOLVIMENTO'),
                        NOME_CPF=input_values.get('NOME CPF'),
                        SEXO=input_values.get('SEXO'),
                        OPERACAO=input_values.get('OPERACAO'),
                        ATIVIDADE=input_values.get('ATIVIDADE'),
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
            expander_label = f"~~{expander_label}~~ (Excluído)"

        with st.expander(expander_label, expanded=False):
            key_prefix = f"deleted_{idx}" if is_deleted else f"extracted_{idx}"

            with st.form(key=f'{key_prefix}_form'):
                submitted = False
                delete_submitted = False
                restore_submitted = False

                input_values = {}
                cols_form = st.columns(num_columns, gap="small")
                for i, coluna in enumerate(colunas):
                    valor = item.get(coluna, '')
                    disabled = is_deleted
                    with cols_form[i % num_columns]:
                        st.markdown('<div class="compact-input">', unsafe_allow_html=True)
                        input_value = st.text_input(
                            label=coluna,
                            value=valor if valor is not None else '',
                            key=f"{key_prefix}_{coluna}",
                            disabled=disabled
                        )
                        st.markdown('</div>', unsafe_allow_html=True)
                        input_values[coluna] = input_value

                col_buttons = st.columns([1, 1])
                with col_buttons[0]:
                    if not is_deleted:
                        submitted = st.form_submit_button("Salvar")
                    else:
                        restore_submitted = st.form_submit_button("Restaurar")

                with col_buttons[1]:
                    if not is_deleted:
                        delete_submitted = st.form_submit_button("Excluir")
                    else:
                        st.write("")

                if not is_deleted and submitted:
                    data = NoticiaRaspadaNomeCreateSchema(
                        CPF=input_values.get('CPF'),
                        NOME=input_values.get('NOME'),
                        APELIDO=input_values.get('APELIDO'),
                        SEXO=input_values.get('SEXO'),
                        # ENVOLVIMENTO=input_values.get('ENVOLVIMENTO'),
                        NOME_CPF=input_values.get('NOME CPF'),
                        OPERACAO=input_values.get('OPERACAO'),
                        ATIVIDADE=input_values.get('ATIVIDADE'),
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
def msg_confirma(msg):
    st.toast(msg, icon="✅")

cols = st.columns([1, 1, 1, 6, 1, 1, 1])
with cols[0]:
    if st.button('Gravar', use_container_width=True):
        update_data = NoticiaRaspadaUpdateSchema(
            FONTE=fonte,
            TITULO=titulo,
            CATEGORIA=categoria,
            REGIAO=regiao,
            UF=uf
        )

        try:
            noticia_service.atualizar_noticia(noticia.ID, update_data)
            msg_confirma('Notícia gravada com sucesso!')
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao gravar a notícia: {e}")
with cols[1]:
    if st.button('Finalizar', use_container_width=True):
        update_data = NoticiaRaspadaUpdateSchema(STATUS='10-URL-OK')
        noticia_service.atualizar_noticia(noticia.ID, update_data)
        msg_confirma('Notícia finalizada')
# with cols[2]:
#     if st.button('Registrar', use_container_width=True):
#         msg_confirma('Registro efetuado')
with cols[6]:
    if st.button('Sair', use_container_width=True):
        st.switch_page("Home.py")
        msg_confirma('Saindo da aplicação')
