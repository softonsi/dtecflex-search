from datetime import date, timedelta
from dateutil import parser
from backend.resources.search_term.search_term_service import SearchTermService
from streamlit_tags import st_tags
from backend.resources.notice.noticia import NoticiaRaspadaUpdateSchema
from backend.resources.notice.noticia_service import NoticiaService
from view_components.services.extract_page.page_content_fetcher import PageContentFetcher
from view_components.services.search_page.RssSerarch import gerer_link, parse_rss_feed
from playwright.sync_api import sync_playwright
from database import SessionLocal
import hashlib
import feedparser
import pandas as pd
import requests
import streamlit as st
import re
from database import SessionLocal

def salvar_filtro(categoria, tags_chave_and, tags_chave_or):
    session = SessionLocal()
    
    try:
        print('tags_chave_and', tags_chave_and)
        print('tags_chave_or', tags_chave_or)
        termo_busca_service = SearchTermService(session)
        termo_busca_service.save(categoria, tags_chave_and, tags_chave_or)
        
        st.success("Filtro salvo com sucesso no banco de dados!")
    except Exception as e:
        st.error(f"Erro ao salvar filtro: {e}")
    finally:
        session.close()

st.set_page_config(
    page_title="Pesquisa",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

page_title = "Pesquisa"
menu_icone = "search"

nome_script_atual = __file__

MAX_SELECTIONS = 2

def get_redirected_url(initial_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        redirection_url = None

        def on_frame_navigated(frame):
            nonlocal redirection_url
            if frame == page.main_frame and "news.google.com" not in frame.url:
                redirection_url = frame.url
                print(f"Redirecionado para: {redirection_url}")

                page.remove_listener("framenavigated", on_frame_navigated)

        page.on("framenavigated", on_frame_navigated)

        page.goto(initial_url)

        for _ in range(60):
            if redirection_url is not None:
                break
            page.wait_for_timeout(500)

        browser.close()

        return redirection_url

def download_html(url, html_content):
    filename = re.sub(r'\W+', '_', url) + ".html"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML salvo como {filename}")

def gerar_tabela(query_pattern):
    response = requests.get(query_pattern)
    feed = feedparser.parse(response.text)
    df = pd.DataFrame(parse_rss_feed(feed))

    df['published'] = df['published'].apply(lambda x: parser.parse(x).date())
    df['extracted'] = False

    return df

if 'removed_urls' not in st.session_state:
    st.session_state.removed_urls = []

if 'resultados' not in st.session_state:
    st.session_state.resultados = pd.DataFrame()

if 'selected_items' not in st.session_state:
    st.session_state.selected_items = []

def remove_row(index):
    st.session_state.removed_urls.append(st.session_state.resultados.at[index, 'url'])
    st.session_state.resultados = st.session_state.resultados.drop(index).reset_index(drop=True)
    st.rerun()

@st.dialog("Editar Texto", width="large")
def edit_text_dialog(text):
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

    st.write("Edite o texto da notícia")
    texto_noticia = st.text_area("Texto da Notícia", value=text, height=300)

def main():
    session = SessionLocal()
    termo_busca_service = SearchTermService(session)

    categoria = ''
    keywords = termo_busca_service.get_processed_terms(categoria)

    session.close()

    categoria = ''

    with st.expander('Pesquisa manual'):
        st.subheader("🔎 Pesquisa Manual")

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            categoria = st.selectbox(
                "Categoria:",
                ("", "Lavagem de Dinheiro", "Crime", "Ambiental", "Empresarial"),
                index=0,
                placeholder="Selecione",
            )

        if keywords:
            with col2:
                selected_keywords = st.selectbox(
                    "Selecione os termos-chave:",
                    keywords,
                    index=0,
                    help="Selecione um ou mais termos para sua pesquisa"
                )
        
        with col3:
            dias = st.number_input("Dias de recuo:", min_value=1, max_value=30)

        with col4:
            LANG = st.text_input("Idioma:", value='pt-BR')

        with col4:
            COUNTRY = st.text_input("País:", value='BR')

        col1, col2, col3, col4 = st.columns([3, 3, 1, 1])
        with col1:
            tags_chave_and = st_tags(label="Palavras de busca AND")

        with col2:
            tags_chave_or = st_tags(label="Palavras de busca OR")

        with col3:
            st.markdown(':mag_right:')
            bt_buscar = st.button("Pesquisar")

        with col4:
            st.markdown('🕵🏻‍♀️')
            bt_salvar = st.button("Salvar")

            if bt_salvar:
                if categoria == '':
                    st.warning('Informe a Categoria')
                elif not tags_chave_and and not tags_chave_or:
                    st.warning('Preencha os campos Palavras AND e Palavras OR')
                else:
                    salvar_filtro(categoria, tags_chave_and, tags_chave_or)

    if dias:
        ref_data = date.today() - timedelta(days=dias)
        st.text(ref_data)
    st.write("URL Removida:", st.session_state.removed_urls)

    st.write("Títulos selecionados:", st.session_state.selected_items)

    bt_save_notice = st.button("Salvar notícia")
    with st.spinner('Carregando links'):
        if (tags_chave_and or tags_chave_or) and bt_buscar:
            link = gerer_link(dias, LANG, COUNTRY, tags_chave_and, tags_chave_or)
            resultados = gerar_tabela(link)
            st.session_state.resultados = resultados
            print('results:::',resultados)
        elif tags_chave_and == [] and tags_chave_or == [] and bt_buscar:
            st.warning('Preencha os campos Palavras AND e Palavras OR')

    if not st.session_state.resultados.empty:
        for i, row in st.session_state.resultados.iterrows():
            key_extracted_text = f'extracted_text_{row["id_original"]}'
            extracted_text = ''
            if key_extracted_text not in st.session_state:
                st.session_state[key_extracted_text] = False

            col1, col2 = st.columns([7, 1])

            with col1.expander(f'''**Fonte da Noticia:** {row['source_title']}
                                    **Titulo:** {row['title']}
                                    **Data de Publicação:** {row['published']}''', expanded=True):
                st.write(f'''
                    {row["url"]}
                    {row['text']}
                ''', unsafe_allow_html=True)

            btn_analyze = col2.button("Analisar", use_container_width=True, type='primary', key=f"btn_analyze_{i}")

            if btn_analyze:
                url = get_redirected_url(row['url'])

                fetcher = PageContentFetcher()
                extracted_text = fetcher.fetch_and_extract_text(url)

                st.session_state[key_extracted_text] = extracted_text

            if col2.button('Remover', key=f'remove_button_{i}', use_container_width=True, type='secondary'):
                remove_row(i)

            if col2.button('Salvar', key=f'save_button_{i}', use_container_width=True, type='secondary'):
                hash_link = hashlib.md5(url.encode('utf-8')).hexdigest()
                session = SessionLocal()
                noticia_service = NoticiaService(session)
                create_data = NoticiaRaspadaUpdateSchema(TEXTO_NOTICIA=extracted_text or None, URL=row['url'], LINK_ID=hash_link, LINK_ORIGINAL=row['url'], DATA_PUBLICACAO=row['published'], FONTE=row['source_title'], CATEGORIA=categoria, QUERY='', ID_ORIGINAL=row['id_original'])
                noticia_service.criar_noticia(create_data)

            if st.session_state[key_extracted_text]:
                btn_show_text = col2.button('Texto notícia', key=f'btn_show_{i}', use_container_width=True)
                if btn_show_text:
                    edit_text_dialog(st.session_state[key_extracted_text])

    st.session_state.selected_items.clear()

if __name__ == "__main__":
    main()
