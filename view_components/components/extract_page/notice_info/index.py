from io import StringIO
import os
import streamlit as st
from backend.resources.notice.noticia import NoticiaRaspadaUpdateSchema
from backend.resources.notice_message_devolute.notice_message_devolute_service import NoticiaRaspadaMsgService
from backend.resources.notice_name.noticia_nome_service import NoticiaNomeService
from backend.resources.notice.noticia_service import NoticiaService
from database import SessionLocal

session = SessionLocal()

noticia_name_service = NoticiaNomeService(session)
noticia_service = NoticiaService(session)

def notice_info(notice):
    if 'page_to_return' not in st.session_state:
        st.session_state['page_to_return'] = 'home.py'

    if notice['mensagens']:
        for msg in notice['mensagens']:
            st.warning(f"NOTÍCIA REPROVADA.\n\n\"{msg.MSG_TEXT}\"", icon="⚠️")

    page_to_return = st.session_state['page_to_return']

    cols = st.columns([1.5, 8, 8])
    with cols[0]:
        if st.button('Voltar', icon=":material/first_page:", use_container_width=True):
            st.switch_page(f"pages/{page_to_return}")
            msg_confirma('Saindo da aplicação')

    st.markdown(f'**URL:** {notice["URL"]}')

    cols_top = st.columns(3)
    with cols_top[0]:
        font = st.text_input('Fonte', value=notice['FONTE'] if notice and notice['FONTE'] else '')
    with cols_top[1]:
        title = st.text_input('Título', value=notice['TITULO'] if notice and notice['TITULO'] else '')
    with cols_top[2]:
        category = st.text_input('Categoria', value=notice['CATEGORIA'] if notice and notice['CATEGORIA'] else '')

    cols_bottom = st.columns(3)
    with cols_bottom[0]:
        region = st.text_input('Região', value=notice['REGIAO'] if notice and hasattr(notice, 'REGIAO') and notice['REGIAO'] else '')
    with cols_bottom[1]:
        uf_list = ['N/A', 'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
                   'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
                   'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
        uf_value = notice['UF'] if notice and hasattr(notice, 'UF') and notice['UF'] in uf_list else 'N/A'
        uf = st.selectbox('UF', options=uf_list, index=uf_list.index(uf_value))
    with cols_bottom[2]:
        arquivo_up = st.file_uploader('Selecione o arquivo')
        if arquivo_up is not None:
            reg_noticia = os.path.splitext(arquivo_up.name)[0]
        else:
            reg_noticia = ''

    main_action_buttons(font, title, category, region, uf, notice['ID'], reg_noticia, page_to_return, notice)

    return font, title, category, region, uf, reg_noticia

def main_action_buttons(font, title, category, region, uf, notice_id, reg_noticia, page_to_return, notice):
    def msg_confirma(msg):
        st.toast(msg, icon="✅")
    
    # Layout com apenas os botões de Excluir e Aprovar
    cols = st.columns([1, 6, 1])
    
    with cols[0]:
        if st.button('Excluir', icon=":material/delete_forever:", use_container_width=True):
            update_data = NoticiaRaspadaUpdateSchema(STATUS='99-DELETED')
            noticia_service.atualizar_noticia(notice_id, update_data)
            msg_confirma('Notícia deletada')
            st.switch_page(f"pages/{page_to_return}")
    
    with cols[2]:
        if st.button('Aprovar', icon=":material/done_all:", type='primary', use_container_width=True):
            # Primeiro, grava as alterações realizadas pelo usuário:
            update_data = NoticiaRaspadaUpdateSchema(
                FONTE=font,
                TITULO=title,
                CATEGORIA=category,
                REGIAO=region,
                UF=uf,
                REG_NOTICIA=reg_noticia
            )
            try:
                noticia_service.atualizar_noticia(notice_id, update_data)
            except Exception as e:
                st.error(f"Erro ao gravar as alterações: {e}")
                return

            # Em seguida, executa a lógica já existente do botão Aprovar
            if notice['mensagens']:
                msg_service = NoticiaRaspadaMsgService(session)
                msg_service.delete_msg(msg_id=notice['mensagens'][0].ID)
            update_data = NoticiaRaspadaUpdateSchema(STATUS='200-TO-APPROVE')
            noticia_service.atualizar_noticia(notice_id, update_data)
            msg_confirma('Notícia finalizada')
            st.switch_page(f"pages/{page_to_return}")
