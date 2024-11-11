import itertools
import streamlit as st

from backend.resources.notice.noticia import NoticiaRaspadaUpdateSchema
from view_components.services.extract_page.text_analyzer import TextAnalyzer

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


def text_with_highlighted_names(text, notice, noticia_service):
    saved_names_list = notice['nomes_raspados']
    if text:
        if not st.session_state.get(f'{notice['ID']}_is_extracted'):
            try:
                with st.spinner('Analisando o texto...'):
                    analyzer = TextAnalyzer()
                    names_results = analyzer.analyze_text(text)

                    st.session_state[f'{notice['ID']}_is_extracted'] = names_results
            except Exception as e:
                print('error', e)
                st.error(f"Erro ao processar a chamada à API: {e}")

        extracted_names_list = st.session_state[f'{notice['ID']}_is_extracted']

        saved_names_set = set([item['NOME'] for item in saved_names_list if 'NOME' in item])
        extracted_names_list = [item for item in extracted_names_list if item.get('NOME') not in saved_names_set]

        names_to_highlight = [
            item['NOME'] 
            for item in saved_names_list + extracted_names_list 
            if 'NOME' in item and isinstance(item['NOME'], str) and item['NOME'].strip()
        ]
        
        with st.expander('Texto notícia e nomes destacados', expanded=True):
            if text and names_to_highlight:
                highlighted_text = destaque_nomes(text, names_to_highlight)
                st.markdown('<div style="font-size:14px; white-space: pre-wrap;">{}</div>'.format(highlighted_text), unsafe_allow_html=True)
            else:
                st.write(notice['TEXTO_NOTICIA'])

            @st.dialog(f"Edite o texto da notícia de id {notice['ID']}", width="large")
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
                        texto_noticia = st.text_area("Texto da Notícia", value=notice['TEXTO_NOTICIA'], height=300)
                        if st.button("Atualizar"):
                            update_data = NoticiaRaspadaUpdateSchema(TEXTO_NOTICIA=texto_noticia)
                            try:
                                noticia_service.atualizar_noticia(notice['ID'], update_data)
                                st.success("Notícia atualizada com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao atualizar a notícia: {e}")

            if "closed_modal" not in st.session_state:
                if st.button("Editar texto"):
                    render_area()

        print('names_to_highlight', names_to_highlight)
        print('saved_names_list', saved_names_list)
        print('extracted_names_list', extracted_names_list)

        return names_to_highlight, saved_names_list, extracted_names_list
