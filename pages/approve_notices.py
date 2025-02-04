import os
import datetime
import pandas as pd
import streamlit as st
from backend.resources.notice.noticia import NoticiaRaspadaUpdateSchema
from backend.resources.notice.noticia_service import NoticiaService
from backend.resources.notice_message_devolute.notice_message_devolute_schema import NoticiaRaspadaMsgCreateSchema
from backend.resources.notice_message_devolute.notice_message_devolute_service import NoticiaRaspadaMsgService
from backend.resources.user.user_service import UserService
from backend.resources.notice_name.noticia_nome_service import NoticiaNomeService
from view_components.middleware.check_auth import require_authentication
from view_components.components.shared.navsidebar import navsidebar
from database import SessionLocal

# Cria a sessão e os serviços
session = SessionLocal()
user_service = UserService(session)
noticia_service = NoticiaService(session)
noticia_raspada_msg_service = NoticiaRaspadaMsgService(session)
noticia_nome_service = NoticiaNomeService(session)

@require_authentication
def main(current_user=None):
    st.set_page_config(page_title="Aprovar Notícias", layout="wide")
    navsidebar(current_user)

    users = user_service.find_all()
    user_options = ["-"] + [user.USERNAME for user in users]

    if 'selected_period' not in st.session_state:
        st.session_state['selected_period'] = "-"
    if 'selected_user' not in st.session_state:
        st.session_state['selected_user'] = "-"
    if 'page' not in st.session_state:
        st.session_state['page'] = 1

    col_title, col_filters = st.columns([3, 2])
    with col_title:
        selected_user = st.sidebar.selectbox(
            "Usuário:",
            user_options,
            index=user_options.index(st.session_state['selected_user'])
                  if st.session_state['selected_user'] in user_options else 0,
            key='selected_user'
        )

    if st.session_state['selected_period'] != "-" or st.session_state['selected_user'] != "-":
        st.session_state['page'] = 1

    filters = {'STATUS': ['200-TO-APPROVE']}
    if st.session_state['selected_period'] and st.session_state['selected_period'] != "-":
        filters['PERIODO'] = st.session_state['selected_period'].lower()
    if st.session_state['selected_user'] and st.session_state['selected_user'] != "-":
        selected_username = st.session_state['selected_user']
        selected_user_obj = next((user for user in users if user.USERNAME == selected_username), None)
        filters['USUARIO_ID'] = selected_user_obj.ID

    per_page = 10
    page = st.session_state['page']

    with st.spinner('Carregando notícias...'):
        noticias, total_count = noticia_service.listar_noticias(
            page=page,
            per_page=per_page,
            filters=filters
        )

    total_pages = (total_count + per_page - 1)

    if 'dialog_nome' not in st.session_state:
        st.session_state['dialog_nome'] = None

    # ---------------------------
    # Barra de Tarefas no Topo
    # ---------------------------
    if noticias:
        with st.container():
            col_taskbar = st.columns([6, 2])
            with col_taskbar[0]:
                if st.button("Aprovar Todas as Notícias", key="approve_all"):
                    with st.spinner("Aprovando todas as notícias..."):
                        for noticia in noticias:
                            update_data = NoticiaRaspadaUpdateSchema(STATUS='201-APPROVED')
                            noticia_service.atualizar_noticia(noticia.ID, update_data)
                    st.toast("Todas as notícias foram aprovadas!")
                    st.rerun()
        st.divider()

    # ---------------------------
    # Exibição de Notícias
    # ---------------------------
    if noticias:
        for noticia in noticias:
            with st.container():
                st.markdown(f"###### Data Publicação: {noticia.DATA_PUBLICACAO.strftime('%d/%m/%Y')}")
                if hasattr(noticia, 'URL'):
                    st.markdown(f"**URL:** {noticia.URL}")

                col_top1, col_top2, col_top3 = st.columns(3)
                with col_top1:
                    font = st.text_input("Fonte", value=noticia.FONTE, key=f"fonte_{noticia.ID}")
                with col_top2:
                    title = st.text_input("Título", value=noticia.TITULO, key=f"titulo_{noticia.ID}")
                with col_top3:
                    category = st.text_input("Categoria", value=noticia.CATEGORIA, key=f"categoria_{noticia.ID}")

                col_bottom1, col_bottom2, col_bottom3 = st.columns(3)
                with col_bottom1:
                    region = st.text_input("Região", value=noticia.REGIAO if noticia.REGIAO else "", key=f"regiao_{noticia.ID}")
                with col_bottom2:
                    uf_list = ['N/A', 'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
                               'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
                               'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
                    uf_value = noticia.UF if noticia.UF in uf_list else 'N/A'
                    uf = st.selectbox("UF", options=uf_list, index=uf_list.index(uf_value), key=f"uf_{noticia.ID}")
                with col_bottom3:
                    reg_noticia = noticia.REG_NOTICIA if noticia.REG_NOTICIA else ""
                    st.text_input("Número do Registro da Notícia (já existente)", value=reg_noticia if reg_noticia else 'NÃO PREENCHIDO', key=f"reg_noticia_{noticia.ID}", disabled=True)
                    arquivo_up = st.file_uploader("SELECIONE O ARQUIVO", key=f"file_{noticia.ID}", label_visibility="hidden")
                    
                    if arquivo_up is not None:
                        reg_noticia = os.path.splitext(arquivo_up.name)[0]
                    else:
                        reg_noticia = noticia.REG_NOTICIA if noticia.REG_NOTICIA else ""
                    
                card_height = 300
                st.text_area(
                    label="Texto da Notícia:",
                    value=noticia.TEXTO_NOTICIA,
                    height=card_height - 40,
                    key=f"text_{noticia.ID}",
                    disabled=True
                )

                if noticia.nomes_raspados:
                    nomes_data = []
                    for nome_obj in noticia.nomes_raspados:
                        nomes_data.append({
                            "ID": nome_obj.ID,
                            "Nome": nome_obj.NOME,
                            "CPF": nome_obj.CPF,
                            "Apelido": nome_obj.APELIDO,
                            "Nome/CPF": nome_obj.NOME_CPF,
                            "Sexo": nome_obj.SEXO,
                            "Pessoa": nome_obj.PESSOA,
                            "Idade": nome_obj.IDADE,
                            "Aniversário": nome_obj.ANIVERSARIO,
                            "Atividade": nome_obj.ATIVIDADE,
                            "Envolvimento": nome_obj.ENVOLVIMENTO,
                            "Tipo de Suspeita": nome_obj.TIPO_SUSPEITA,
                            "Pessoa Pública": nome_obj.FLG_PESSOA_PUBLICA,
                            "Indicador PPE": nome_obj.INDICADOR_PPE,
                            "Operação": nome_obj.OPERACAO
                        })
                    df_nomes = pd.DataFrame(nomes_data)
                    st.table(df_nomes)
                else:
                    st.write("Nenhum nome extraído.")

                action_cols = st.columns([1.2, 1, 8])
                # Exemplo de botão para salvar a notícia (comentado)
                # with action_cols[0]:
                #     if st.button("Salvar Notícia", key=f"salvar_{noticia.ID}"):
                #         update_data = NoticiaRaspadaUpdateSchema(
                #             FONTE=font,
                #             TITULO=title,
                #             CATEGORIA=category,
                #             REGIAO=region,
                #             UF=uf,
                #             REG_NOTICIA=reg_noticia
                #         )
                #         try:
                #             noticia_service.atualizar_noticia(noticia.ID, update_data)
                #             st.toast("Notícia gravada com sucesso!")
                #             st.rerun()
                #         except Exception as e:
                #             st.error(f"Erro ao gravar a notícia: {e}")=
                with action_cols[0]:
                    if st.button("Devolver para análise", key=f"devolver_{noticia.ID}"):
                        open_justificativa_dialog(noticia, current_user)
                with action_cols[1]:
                    if st.button("Editar Nomes", key=f"editar_nomes_{noticia.ID}"):
                        edit_nomes_dialog(noticia)

                st.divider()
    else:
        st.write("Nenhuma notícia encontrada para os filtros selecionados.")

    # Paginação
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

@st.dialog("Justificativa para Devolução")
def open_justificativa_dialog(noticia, current_user):
    justificativa = st.text_area("Digite sua justificativa para a devolução da notícia:", height=200)
    if st.button("Enviar Justificativa"):
        if justificativa.strip():
            msg_data = NoticiaRaspadaMsgCreateSchema(MSG_TEXT=justificativa)
            user_id = current_user['user_id']
            noticia_raspada_msg_service.create_msg(
                noticia_id=noticia.ID,
                msg_data=msg_data,
                user_id=user_id
            )
            update_data = NoticiaRaspadaUpdateSchema(STATUS='06-REPROVED')
            noticia_service.atualizar_noticia(noticia.ID, update_data)
            st.toast("Justificativa enviada com sucesso.")
            st.rerun()
        else:
            st.warning("Por favor, forneça uma justificativa antes de enviar.")

@st.dialog("Editar Nomes")
def edit_nomes_dialog(noticia):
    st.markdown("Edite os dados dos nomes extraídos abaixo:")
    for nome_obj in noticia.nomes_raspados:
        with st.expander(f"Nome ID: {nome_obj.ID}", expanded=False):
            updated_nome = st.text_input("Nome", value=nome_obj.NOME, key=f"nome_edit_{nome_obj.ID}_NOME")
            updated_cpf = st.text_input("CPF", value=nome_obj.CPF, key=f"nome_edit_{nome_obj.ID}_CPF")
            updated_nome_cpf = st.text_input("Nome/CPF", value=nome_obj.NOME_CPF, key=f"nome_edit_{nome_obj.ID}_NOME_CPF")
            updated_apelido = st.text_input("Apelido", value=nome_obj.APELIDO, key=f"nome_edit_{nome_obj.ID}_APELIDO")
            updated_sexo = st.text_input("Sexo", value=nome_obj.SEXO, key=f"nome_edit_{nome_obj.ID}_SEXO")
            updated_pessoa = st.text_input("Pessoa", value=nome_obj.PESSOA, key=f"nome_edit_{nome_obj.ID}_PESSOA")
            updated_idade = st.number_input("Idade", value=nome_obj.IDADE if nome_obj.IDADE is not None else 0, key=f"nome_edit_{nome_obj.ID}_IDADE", min_value=0)
            updated_atividade = st.text_input("Atividade", value=nome_obj.ATIVIDADE, key=f"nome_edit_{nome_obj.ID}_ATIVIDADE")
            updated_envolvimento = st.text_area("Envolvimento", value=nome_obj.ENVOLVIMENTO, key=f"nome_edit_{nome_obj.ID}_ENVOLVIMENTO")
            updated_tipo_suspeita = st.text_input("Tipo de Suspeita", value=nome_obj.TIPO_SUSPEITA, key=f"nome_edit_{nome_obj.ID}_TIPO_SUSPEITA")
            updated_flg_pessoa_publica = st.checkbox(
                "Pessoa Pública",
                value=True if nome_obj.FLG_PESSOA_PUBLICA in ["S", "True", "true"] else False,
                key=f"nome_edit_{nome_obj.ID}_FLG_PESSOA_PUBLICA"
            )
            updated_indicador_ppe = st.checkbox(
                "Indicador PPE",
                value=True if nome_obj.INDICADOR_PPE in ["S", "True", "true"] else False,
                key=f"nome_edit_{nome_obj.ID}_INDICADOR_PPE"
            )
            default_date = nome_obj.ANIVERSARIO if nome_obj.ANIVERSARIO is not None else datetime.date.today()
            updated_aniversario = st.date_input("Aniversário", value=default_date, key=f"nome_edit_{nome_obj.ID}_ANIVERSARIO")
            st.divider()
    if st.button("Salvar Alterações"):
        for nome_obj in noticia.nomes_raspados:
            new_data = {
                "NOME": st.session_state.get(f"nome_edit_{nome_obj.ID}_NOME", nome_obj.NOME),
                "CPF": st.session_state.get(f"nome_edit_{nome_obj.ID}_CPF", nome_obj.CPF),
                "NOME_CPF": st.session_state.get(f"nome_edit_{nome_obj.ID}_NOME_CPF", nome_obj.NOME_CPF),
                "APELIDO": st.session_state.get(f"nome_edit_{nome_obj.ID}_APELIDO", nome_obj.APELIDO),
                "SEXO": st.session_state.get(f"nome_edit_{nome_obj.ID}_SEXO", nome_obj.SEXO),
                "PESSOA": st.session_state.get(f"nome_edit_{nome_obj.ID}_PESSOA", nome_obj.PESSOA),
                "IDADE": st.session_state.get(f"nome_edit_{nome_obj.ID}_IDADE", nome_obj.IDADE),
                "ATIVIDADE": st.session_state.get(f"nome_edit_{nome_obj.ID}_ATIVIDADE", nome_obj.ATIVIDADE),
                "ENVOLVIMENTO": st.session_state.get(f"nome_edit_{nome_obj.ID}_ENVOLVIMENTO", nome_obj.ENVOLVIMENTO),
                "TIPO_SUSPEITA": st.session_state.get(f"nome_edit_{nome_obj.ID}_TIPO_SUSPEITA", nome_obj.TIPO_SUSPEITA),
                "FLG_PESSOA_PUBLICA": "S" if st.session_state.get(f"nome_edit_{nome_obj.ID}_FLG_PESSOA_PUBLICA", False) else "N",
                "ANIVERSARIO": st.session_state.get(f"nome_edit_{nome_obj.ID}_ANIVERSARIO", nome_obj.ANIVERSARIO),
                "INDICADOR_PPE": "S" if st.session_state.get(f"nome_edit_{nome_obj.ID}_INDICADOR_PPE", False) else "N"
            }
            try:
                noticia_nome_service.atualizar_nome(nome_obj.ID, new_data)
            except Exception as e:
                st.error(f"Erro ao atualizar nome ID {nome_obj.ID}: {e}")
        st.toast("Nomes atualizados com sucesso!")
        st.rerun()

if __name__ == "__main__":
    main()
