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

uf_list = ['N/A', 'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
                   'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
                   'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']

def notice_info(notice):
    if 'page_to_return' not in st.session_state:
        st.session_state['page_to_return'] = 'home.py'
    page_to_return = st.session_state['page_to_return']

    if notice['mensagens']:
        for msg in notice['mensagens']:
            st.warning(f"NOTÍCIA REPROVADA.\n\n\"{msg.MSG_TEXT}\"", icon="⚠️")

    cols_voltar = st.columns([1.5, 8, 8])
    with cols_voltar[0]:
        if st.button('Voltar', icon=":material/first_page:", use_container_width=True):
            unsaved = False
            if st.session_state.get('font_input', '') != (notice.get('FONTE') or ''):
                unsaved = True
            if st.session_state.get('title_input', '') != (notice.get('TITULO') or ''):
                unsaved = True
            if st.session_state.get('category_input', '') != (notice.get('CATEGORIA') or ''):
                unsaved = True
            if st.session_state.get('region_input', '') != (notice.get('REGIAO') or ''):
                unsaved = True
            if st.session_state.get('uf_input', 'N/A') != (notice.get('UF') if notice.get('UF') in uf_list else 'N/A'):
                unsaved = True
            # if reg_noticia != '':
            #     unsaved = True

            if unsaved:
                st.toast("Você tem alterações não salvas. Por favor, salve ou descarte as alterações antes de sair.", icon="⚠️")
            else:
                st.switch_page(f"pages/{page_to_return}")
                st.toast('Saindo da aplicação', icon="✅")
    
    st.markdown(f'**URL:** {notice["URL"]}')

    cols_top = st.columns(3)
    with cols_top[0]:
        font = st.text_input(
            'Fonte',
            value=notice.get('FONTE') or '',
            key='font_input'
        )
    with cols_top[1]:
        title = st.text_input(
            'Título',
            value=notice.get('TITULO') or '',
            key='title_input'
        )
    with cols_top[2]:
        category = st.text_input(
            'Categoria',
            value=notice.get('CATEGORIA') or '',
            key='category_input'
        )

    cols_bottom = st.columns(3)
    with cols_bottom[0]:
        region = st.text_input(
            'Região',
            value=notice.get('REGIAO') or '',
            key='region_input'
        )
    with cols_bottom[1]:
        uf_value = notice.get('UF') if notice.get('UF') in uf_list else 'N/A'
        uf = st.selectbox(
            'UF',
            options=uf_list,
            index=uf_list.index(uf_value),
            key='uf_input'
        )
    with cols_bottom[2]:
        arquivo_up = st.file_uploader('Selecione o arquivo', key='arquivo_up')
        if arquivo_up is not None:
            reg_noticia = os.path.splitext(arquivo_up.name)[0]
        else:
            reg_noticia = ''

    main_action_buttons(
        st.session_state.get('font_input', ''),
        st.session_state.get('title_input', ''),
        st.session_state.get('category_input', ''),
        st.session_state.get('region_input', ''),
        st.session_state.get('uf_input', 'N/A'),
        notice['ID'],
        reg_noticia,
        page_to_return,
        notice
    )

    return (
        st.session_state.get('font_input', ''),
        st.session_state.get('title_input', ''),
        st.session_state.get('category_input', ''),
        st.session_state.get('region_input', ''),
        st.session_state.get('uf_input', 'N/A'),
        reg_noticia
    )

def main_action_buttons(font, title, category, region, uf, notice_id, reg_noticia, page_to_return, notice):
    def msg_confirma(msg):
        st.toast(msg, icon="✅")
    
    cols = st.columns([1, 6, 1])
    
    with cols[0]:
        if st.button('Excluir', icon=":material/delete_forever:", use_container_width=True):
            update_data = NoticiaRaspadaUpdateSchema(STATUS='99-DELETED')
            noticia_service.atualizar_noticia(notice_id, update_data)
            msg_confirma('Notícia deletada')
            st.switch_page(f"pages/{page_to_return}")
    
    with cols[2]:
        if st.button('Aprovar', icon=":material/done_all:", type='primary', use_container_width=True):
            if not font or not title or not category or not region or not reg_noticia:
                st.toast("Todos os campos devem ser preenchidos antes de aprovar a notícia.", icon="⚠️")
                return
            
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

            if notice['mensagens']:
                msg_service = NoticiaRaspadaMsgService(session)
                msg_service.delete_msg(msg_id=notice['mensagens'][0].ID)
            
            update_data = NoticiaRaspadaUpdateSchema(STATUS='200-TO-APPROVE')
            noticia_service.atualizar_noticia(notice_id, update_data)
            msg_confirma('Notícia finalizada')
            st.switch_page(f"pages/{page_to_return}")
