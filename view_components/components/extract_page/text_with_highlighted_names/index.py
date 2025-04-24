import re
import itertools
import streamlit as st

from backend.resources.notice.noticia import NoticiaRaspadaUpdateSchema
from backend.resources.notice.noticia_service import NoticiaService
from view_components.services.extract_page.text_analyzer import TextAnalyzer
from database import SessionLocal

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
            f'<span style="background-color: {next(color_sequence)}; '
            f'text-transform: uppercase; font-weight: bold;">{nome}</span>'
        )
    texto = texto.replace('\n', '<br>').replace('\r', '<br>')

    return texto

def text_with_highlighted_names(notice_id):
    session = SessionLocal()
    noticia_service = NoticiaService(session)
    notice = noticia_service.get_by_id_with_names(notice_id)
    original_text = notice.get('TEXTO_NOTICIA') or ''

    visual_text = re.sub(r'R\$', r'R\\$', original_text)

    saved_names_list = notice.get('nomes_raspados') or []
    extracted_names_list = []
    names_to_highlight = []

    names_results = st.session_state.get(f'{notice["ID"]}_is_extracted', [])

    with st.expander('**Texto notícia e nomes destacados**', expanded=True):
        if names_results:
            extracted_names_list = names_results
            saved_names_set = {
                item['NOME'] for item in saved_names_list
                if 'NOME' in item and isinstance(item['NOME'], str)
            }
            extracted_names_list = [
                item for item in extracted_names_list
                if item.get('NOME') not in saved_names_set
            ]

            names_to_highlight = [
                item['NOME']
                for item in saved_names_list + extracted_names_list
                if isinstance(item.get('NOME'), str) and item['NOME'].strip()
            ]

        if visual_text and names_to_highlight:
            highlighted = destaque_nomes(visual_text, names_to_highlight)
            st.markdown(
                f'<div style="font-size:14px; white-space: pre-wrap;">{highlighted}</div>',
                unsafe_allow_html=True
            )
        else:
            if visual_text:
                if len(visual_text) == 0:
                    st.write('Não há texto para exibir.')
                else:
                    st.markdown(visual_text, unsafe_allow_html=True)

        col_analisar, col_editar, _ = st.columns([2, 2, 6])
        with col_analisar:
            if st.button("Analisar", icon=":material/find_in_page:", use_container_width=True):
                try:
                    with st.spinner('Analisando o texto...'):
                        analyser = TextAnalyzer(notice_categoria=notice['CATEGORIA'])
                        results = analyser.analyze_text(original_text)
                        if not results:
                            st.toast('Texto analisado e nenhum nome encontrado.')
                        st.session_state[f'{notice["ID"]}_is_extracted'] = results
                        st.toast("Análise concluída!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro ao processar a chamada à API: {e}")
        with col_editar:
            if st.button("Editar", icon=":material/edit_note:", use_container_width=True):
                edit_text_dialog(notice, noticia_service)
    return (
        names_to_highlight,
        saved_names_list,
        extracted_names_list
    )

@st.dialog("Editar Texto", width="large")
def edit_text_dialog(notice, noticia_service):
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

    texto_noticia = st.text_area(
        "Texto da Notícia",
        value=notice.get('TEXTO_NOTICIA', ''),
        height=500
    )
    if st.button("Atualizar", use_container_width=True):
        update_data = NoticiaRaspadaUpdateSchema(TEXTO_NOTICIA=texto_noticia)
        try:
            noticia_service.atualizar_noticia(notice['ID'], update_data)
            st.success("Notícia atualizada com sucesso!")
            st.session_state['texto_atualizado'] = True
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao atualizar a notícia: {e}")
