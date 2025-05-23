from datetime import date, datetime
import hashlib
import uuid
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
    st.set_page_config(page_title="Página inicial", layout='wide')
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

@require_authentication
def main(current_user=None):
    init_page_layout()
    navsidebar(current_user)

    contagens = noticia_name_service.obter_contagem_por_status()
    st.markdown("## 📊 Contagem de nomes por notícia")
    contagens = noticia_name_service.obter_contagem_por_status()

    label_map = {
        "205-TRANSFERED": "Transferidas",
        "200-TO-APPROVE": "Aguardando aprovação",
        "201-APPROVED": "Aprovadas Hoje",
        "203-PUBLISHED": "Publicadas",
    }

    cols = st.columns(len(contagens))
    for col, (status, count) in zip(cols, contagens.items()):
        label = label_map.get(status, status)
        # aqui não passamos href direto, mas usamos onclick + JS
        html = f"""
        <div style="text-align:center;">
        <a style="text-decoration:none; color:inherit; cursor:pointer;"
            onclick="
            window.location.href = window.location.origin
                + '/list_names_per_status?status_to_list={status}';
            ">
            <span style="font-size:2rem; font-weight:bold;">{count}</span>
        </a>
        <div style="font-size:0.9rem; color:#555;">{label}</div>
        </div>
        """
        col.markdown(html, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('#### <i class="bi bi-newspaper"></i> Notícias', unsafe_allow_html=True)
    
    session = SessionLocal()
    noticia_service = NoticiaService(session)

    if 'edit_mode' not in st.session_state:
        st.session_state['edit_mode'] = False
    if 'edit_id' not in st.session_state:
        st.session_state['edit_id'] = None

    def listar_noticias():
        noticias, total_pages = filters(session)

        cols = st.columns([4,10,1,1,1])
        with cols[0]:
            if st.button('Incluir', icon=":material/newspaper:", type='primary'):
                notice_register_dialog()
        with cols[2]:
            if st.button("", icon=":material/chevron_backward:", disabled=st.session_state['page_number'] <= 1):
                st.session_state['page_number'] -= 1
                st.rerun()
        with cols[3]:
            st.markdown(
                f"<div style='text-align: center; padding-top: 10px;'>{st.session_state['page_number']} - {total_pages}</div>",
                unsafe_allow_html=True
            )
        with cols[4]:
            if st.button("", icon=":material/chevron_forward:", disabled=st.session_state['page_number'] >= total_pages):
                st.session_state['page_number'] += 1
                st.rerun()

        if noticias:
            noticias_data = [noticia.model_dump() for noticia in noticias]

            for noticia in noticias_data:
                col1, col2 = st.columns([ 7, 1])

                st.markdown(f'[{noticia["ID"]}]', unsafe_allow_html=True)
                with col1:
                    st.markdown(render_box('Título', noticia['TITULO']), unsafe_allow_html=True)
                    st.markdown(render_box('Fonte', noticia['FONTE']), unsafe_allow_html=True)
                    st.markdown(f'**Link Google:** [Acessar link]({noticia["LINK_ORIGINAL"]})')

                    key_edit_mode = f"edit_mode_{noticia['ID']}"
                    if key_edit_mode not in st.session_state:
                        st.session_state[key_edit_mode] = False

                    if noticia['URL'] is None or noticia['STATUS'] == '15-URL-CHK' or st.session_state[key_edit_mode]:
                        with st.form(key=f"link_form_{noticia['ID']}"):
                            link_col, button_col = st.columns([10, 1])
                            with link_col:
                                link = st.text_input('**Link Notícia**', value=noticia.get('URL', ''), label_visibility="collapsed")
                            with button_col:
                                salvar_link = st.form_submit_button('', icon=":material/save:")

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
                        link_col, button_col = st.columns([9, 1])
                        with link_col:
                            st.markdown(f'**Link Notícia:** [{noticia["URL"]}]({noticia["URL"]})')
                        with button_col:
                            if st.button('', icon=":material/edit_note:", key=f"edit_link_{noticia['ID']}"):
                                st.session_state[key_edit_mode] = True
                                st.rerun()

                    xcol1, xcol2, _ = st.columns([1, 1, 3])
                    with xcol1:
                        if noticia['STATUS'] == '99-DELETED':
                            if st.button("Recuperar", key=f"recuperar_{noticia['ID']}_{st.session_state['page_number']}"):
                                update_data = NoticiaRaspadaUpdateSchema(STATUS='15-URL-CHK')
                                noticia_service.atualizar_noticia(noticia['ID'], update_data)
                                st.toast(f"Notícia ID {noticia['ID']} recuperada com sucesso.")
                                st.rerun()
                        else:
                            if st.button("Excluir", icon=":material/delete_forever:", key=f"delete_{noticia['ID']}_{st.session_state['page_number']}"):
                                update_data = NoticiaRaspadaUpdateSchema(STATUS='99-DELETED')
                                noticia_service.atualizar_noticia(noticia['ID'], update_data)
                                st.toast(f"Notícia ID {noticia['ID']} excluída com sucesso.")
                                st.rerun()
                    with xcol2:
                        if st.button("Analisar", icon=":material/find_in_page:", key=f"analisar_{noticia['ID']}_{st.session_state['page_number']}", disabled=not (noticia['STATUS'] == '10-URL-OK' or noticia['STATUS'] == '07-EDIT-MODE')):
                            with st.spinner("Analisando..."):
                                st.session_state['page_to_return'] = 'home.py'
                                st.session_state['id_notice_to_analyze'] = noticia['ID']
                                st.session_state[f'notice_to_analyze_{noticia["ID"]}'] = noticia
                                st.session_state['url'] = noticia['URL']
                                st.switch_page("pages/_extract_page.py")

                with col2:
                    st.markdown(render_status('Status', noticia['STATUS']), unsafe_allow_html=True)
                    st.markdown(render_box('Categoria', noticia['CATEGORIA']), unsafe_allow_html=True)
                    st.markdown(render_box('Publicação', noticia['DATA_PUBLICACAO']), unsafe_allow_html=True)
                    st.markdown(render_box('Extração', noticia['DT_RASPAGEM']), unsafe_allow_html=True)

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
            margin-bottom: 2px;">
            {txt_label} 
        </label>
        <div style="
            font-weight: bold;
            background-color: #fbfbfb;
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

    if '99-' in txt:  # Vermelho
        bg_color = '#f8d7da'
    elif '10-' in txt:  # Verde
        bg_color = '#b2e6b2'
    elif '15-' in txt:  # Amarelo
        bg_color = '#fff3cd'
    elif '07-' in txt:  # Amarelo
        bg_color = '#fff3cd'
    else:  # default / neutro
        bg_color = '#fff8e1'

    return f"""
    <div style="
        display: flex;
        flex-direction: column;
        margin-bottom: 15px;
    ">
        <label style="
            font-size: 14px;
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

@st.dialog("Você possui alterações não salvas.")
def notice_register_dialog():
    st.write("Preencha os campos para registrar a notícia.")

    if "url_input" not in st.session_state:
        st.session_state["url_input"] = ""
    if "fonte_input" not in st.session_state:
        st.session_state["fonte_input"] = ""
    if "categoria_input" not in st.session_state:
        st.session_state["categoria_input"] = ""
    if "titulo_input" not in st.session_state:
        st.session_state["titulo_input"] = ""

    url = st.text_input("URL", key="url_input")
    fonte_input = st.text_input("Fonte", key="fonte_input")
    categoria_input = st.selectbox("Categoria:", ["", "Lavagem de Dinheiro", "Crime", "Ambiental", "Empresarial", "Fraude"], index=0, key="categoria_input")
    titulo = st.text_input("Título", key="titulo_input")

    noticia_data = NoticiaRaspadaBaseSchema(
        LINK_ID=generate_hash(),
        URL=url.strip() if url else None,
        FONTE=fonte_input.strip(),
        DATA_PUBLICACAO=datetime.now(),
        CATEGORIA=categoria_input.strip(),
        QUERY="",
        ID_ORIGINAL=generate_hash(),
        DT_RASPAGEM=datetime.now(),
        TITULO=titulo.strip() if titulo else None,
        LINK_ORIGINAL=None,
        UF=None,
        REGIAO=None,
        TEXTO_NOTICIA=None,
        STATUS="10-URL-OK"
    )

    cols = st.columns([1, 1])
    with cols[0]:
        if st.button("Ir para notícia", use_container_width=True):
            try:
                created_notice = noticia_service.criar_noticia(noticia_data)
                st.session_state['page_to_return'] = 'home.py'
                st.session_state['id_notice_to_analyze'] = created_notice.ID
                st.session_state[f'notice_to_analyze_{created_notice.ID}'] = created_notice
                st.session_state['url'] = created_notice.URL
                st.session_state['page_number'] = 1
                st.switch_page("pages/_extract_page.py")
            except Exception as e:
                st.error(f"Erro ao criar notícia: {e}")

    with cols[1]:
        if st.button("Continuar cadastro", use_container_width=True):
            try:
                created_notice = noticia_service.criar_noticia(noticia_data)
                st.session_state['page_number'] = 1
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao criar notícia: {e}")

if __name__ == "__main__":
    main()
