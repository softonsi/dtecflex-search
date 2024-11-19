import streamlit as st
from backend.resources.notice.noticia import NoticiaRaspadaUpdateSchema
from backend.resources.notice.noticia_service import NoticiaService
from backend.resources.user.user_service import UserService
from view_components.middleware.check_auth import require_authentication
from view_components.components.shared.navsidebar import navsidebar
from database import SessionLocal

@require_authentication
def main(current_user=None):
    st.set_page_config(page_title="Aprovar notícias", layout="wide")
    navsidebar()
    session = SessionLocal()
    user_service = UserService()
    noticia_service = NoticiaService(session)

    users = user_service.find_all()
    user_options = ["-"] + [user.USUARIO for user in users]

    if 'selected_period' not in st.session_state:
        st.session_state['selected_period'] = "-"
    if 'selected_user' not in st.session_state:
        st.session_state['selected_user'] = "-"
    if 'page' not in st.session_state:
        st.session_state['page'] = 1

    col_title, col_filters = st.columns([3, 2])

    with col_title:
        col_user, col_period = st.columns(2)
        # with col_period:
        #     period_options = ["-", "Hoje", "Última semana", "Último mês"]
        #     selected_period = st.selectbox(
        #         "Período:",
        #         period_options,
        #         index=period_options.index(st.session_state['selected_period']) if st.session_state['selected_period'] in period_options else 0,
        #         key='selected_period'
        #     )

        # with col_user:
    selected_user = st.sidebar.selectbox(
        "Usuário:",
        user_options,
        index=user_options.index(st.session_state['selected_user']) if st.session_state['selected_user'] in user_options else 0,
        key='selected_user'
    )

    if st.session_state['selected_period'] != "-" or st.session_state['selected_user'] != "-":
        st.session_state['page'] = 1

    filters = {}

    filters['STATUS'] = ['200-TO-APPROVE']

    if st.session_state['selected_period'] and st.session_state['selected_period'] != "-":
        filters['PERIODO'] = st.session_state['selected_period'].lower()

    if st.session_state['selected_user'] and st.session_state['selected_user'] != "-":
        selected_username = st.session_state['selected_user']
        selected_user2 = next((user for user in users if user.USUARIO == selected_username), None)
        filters['USUARIO_ID'] = selected_user2.ID

    per_page = 10
    page = st.session_state['page']

    with st.spinner('Carregando notícias...'):
        noticias, total_count = noticia_service.listar_noticias(
            page=page,
            per_page=per_page,
            filters=filters
        )

    total_pages = (total_count + per_page - 1) // per_page

    if 'dialog_nome' not in st.session_state:
        st.session_state['dialog_nome'] = None

    if noticias:
        for noticia in noticias:
            with st.container():
                card_height = 300
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"###### {noticia.TITULO}")
                    st.write(f"Data Publicação: {noticia.DATA_PUBLICACAO.strftime('%d/%m/%Y')}")
                    st.write(f"Fonte: {noticia.FONTE}")
                    st.text_area(
                        label="",
                        value=noticia.TEXTO_NOTICIA,
                        height=card_height - 40,  # Ajuste para a altura do título
                        key=f"text_{noticia.ID}",
                        disabled=False
                    )

                with col2:
                    st.markdown("### Nomes Salvos")
                    if noticia.nomes_raspados:
                        for nome_obj in noticia.nomes_raspados:
                            nome = nome_obj.NOME
                            if st.button(nome, key=f"{nome}_{noticia.ID}"):
                                st.session_state.dialog_nome = nome_obj
                    else:
                        st.write("Nenhum nome raspado.")

                # Exibir o diálogo com as informações do nome selecionado
                if st.session_state.dialog_nome and st.session_state.dialog_nome in noticia.nomes_raspados:
                    @st.dialog(f"Detalhes de {st.session_state.dialog_nome.NOME}")
                    def show_dialog():
                        nome_obj = st.session_state.dialog_nome
                        # Renderizar as informações com labels e inputs
                        st.text_input("ID:", value=nome_obj.ID, key=f"id_{nome_obj.ID}", disabled=True)
                        st.text_input("Nome:", value=nome_obj.NOME, key=f"nome_{nome_obj.ID}", disabled=True)
                        st.text_input("CPF:", value=nome_obj.CPF, key=f"cpf_{nome_obj.ID}", disabled=True)
                        st.text_input("Apelido:", value=nome_obj.APELIDO, key=f"apelido_{nome_obj.ID}", disabled=True)
                        st.text_input("Nome/CPF:", value=nome_obj.NOME_CPF, key=f"nome_cpf_{nome_obj.ID}", disabled=True)
                        st.text_input("Sexo:", value=nome_obj.SEXO, key=f"sexo_{nome_obj.ID}", disabled=True)
                        st.text_input("Pessoa:", value=nome_obj.PESSOA, key=f"pessoa_{nome_obj.ID}", disabled=True)
                        st.number_input("Idade:", value=nome_obj.IDADE, key=f"idade_{nome_obj.ID}", disabled=True)
                        st.date_input("Aniversário:", value=nome_obj.ANIVERSARIO, key=f"aniversario_{nome_obj.ID}", disabled=True)
                        st.text_input("Atividade:", value=nome_obj.ATIVIDADE, key=f"atividade_{nome_obj.ID}", disabled=True)
                        st.text_input("Envolvimento:", value=nome_obj.ENVOLVIMENTO, key=f"envolvimento_{nome_obj.ID}", disabled=True)
                        st.text_input("Tipo de Suspeita:", value=nome_obj.TIPO_SUSPEITA, key=f"tipo_suspeita_{nome_obj.ID}", disabled=True)
                        st.checkbox("Pessoa Pública:", value=nome_obj.FLG_PESSOA_PUBLICA, key=f"pessoa_publica_{nome_obj.ID}", disabled=True)
                        st.checkbox("Indicador PPE:", value=nome_obj.INDICADOR_PPE, key=f"indicador_ppe_{nome_obj.ID}", disabled=True)
                        st.text_input("Operação:", value=nome_obj.OPERACAO, key=f"operacao_{nome_obj.ID}", disabled=True)

                        if st.button("Fechar", key=f"fechar_{nome_obj.ID}"):
                            st.session_state.dialog_nome = None
                            st.rerun()
                    show_dialog()

                if st.button('Aprovar', key=f"aprovar_{noticia.ID}"):
                    update_data = NoticiaRaspadaUpdateSchema(STATUS='201-APPROVED')
                    noticia_service.atualizar_noticia(noticia['ID'], update_data)
                    st.toast('Notícia aprovada')
                    st.rerun()
                st.divider()
    else:
        st.write("Nenhuma notícia encontrada para os filtros selecionados.")

    pagination_placeholder = st.empty()
    with pagination_placeholder:
        col_prev, col_page, col_next = st.columns([1, 2, 1])

        with col_prev:
            if st.button("Anterior") and page > 1:
                st.session_state['page'] -= 1
                st.rerun()

        with col_page:
            st.write(f"**Página {page} de {total_pages}**")


        with col_next:
            if st.button("Próximo") and page < total_pages:
                st.session_state['page'] += 1
                st.rerun()

if __name__ == "__main__":
    main()
