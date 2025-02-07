import streamlit as st
from backend.resources.notice.noticia_service import NoticiaService
from database import SessionLocal
from backend.resources.notice.noticia_repository import NoticiaRepository
from view_components.components.shared.navsidebar import navsidebar
from view_components.middleware.check_auth import require_authentication

session = SessionLocal()
noticia_repository = NoticiaRepository(session)

@require_authentication
def main(current_user=None):
    st.set_page_config(page_title="Minhas análises", layout='wide')
    navsidebar(current_user)

    # Configura valores padrão na session_state, se ainda não existirem
    if 'per_page' not in st.session_state:
        st.session_state['per_page'] = 30
    if 'selected_tab' not in st.session_state:
        st.session_state['selected_tab'] = '07-EDIT-MODE'
    
    per_page = st.session_state.get('per_page', 30)
    
    noticia_service = NoticiaService(session)
    
    status_options = ['07-EDIT-MODE', '200-TO-APPROVE', '06-REPROVED', '201-APPROVED']
    
    # Calcula a contagem correta de notícias para cada status usando o total retornado
    status_counts = {}
    for status in status_options:
        filters_applied = {'STATUS': [status], 'USUARIO_ID': current_user['user_id']}
        # Aqui, o serviço retorna (lista_de_noticias, total_de_noticias)
        _, total_count = noticia_service.listar_noticias(
            page=1,
            per_page=1,  # limitamos a 1 para não carregar muitas notícias, mas o total é calculado internamente
            filters=filters_applied
        )
        status_counts[status] = total_count

    # Layout dos botões das abas
    cols = st.columns([5, 1.4, 1.7, 1.5, 1.4, 5])
    with cols[1]:
        if st.button(f'Em Edição ({status_counts["07-EDIT-MODE"]})', key='edit', help='Notícias em edição'):
            st.session_state['selected_tab'] = '07-EDIT-MODE'
    with cols[2]:
        if st.button(f'Para Aprovação ({status_counts["200-TO-APPROVE"]})', key='approve', help='Notícias para aprovação'):
            st.session_state['selected_tab'] = '200-TO-APPROVE'
    with cols[3]:
        if st.button(f'Reprovadas ({status_counts["06-REPROVED"]})', key='reproved', help='Notícias reprovadas'):
            st.session_state['selected_tab'] = '06-REPROVED'
    with cols[4]:
        if st.button(f'Aprovadas ({status_counts["201-APPROVED"]})', key='approved', help='Notícias aprovadas'):
            st.session_state['selected_tab'] = '201-APPROVED'

    selected_tab = st.session_state['selected_tab']

    # Busca as notícias para a aba selecionada
    filters_applied = {'STATUS': [selected_tab], 'USUARIO_ID': current_user['user_id']}
    noticias, total_noticias = noticia_service.listar_noticias(
        page=st.session_state.get('page_number', 1),
        per_page=per_page,
        filters=filters_applied
    )

    if noticias:
        for noticia in noticias:
            with st.container():
                st.markdown(f"###### {noticia.CATEGORIA}")
                st.markdown(f"###### {noticia.TITULO}")
                st.write(f"Data Publicação: {noticia.DATA_PUBLICACAO.strftime('%d/%m/%Y')}")
                st.write(f"Fonte: {noticia.FONTE}")

                if noticia.mensagens:
                    for mensagem in noticia.mensagens:
                        with st.expander("Detalhes de justificativa", expanded=True):
                            st.text_area(
                                label="",
                                value=mensagem.MSG_TEXT,
                                height=360,  # 400 - 40
                                key=f"just_{noticia.ID}",
                                disabled=True
                            )
                
                cols = st.columns([1, 2, 6, 1, 1])
                with cols[0]:
                    if st.button('Analisar', key=f"analisar_{noticia.ID}"):
                        with st.spinner("Analisando..."):
                            st.session_state['page_to_return'] = 'my_analysis.py'
                            st.session_state['id_notice_to_analyze'] = noticia.ID
                            st.session_state[f'notice_to_analyze_{noticia.ID}'] = noticia
                            st.session_state['url'] = noticia.URL
                            st.switch_page("pages/_extract_page.py")
                
                st.divider()
    else:
        st.write(f"Nenhuma notícia encontrada para o status '{selected_tab}'.")

if __name__ == "__main__":
    main()
