import os
import datetime
import streamlit as st
from database import SessionLocal
from backend.resources.notice.noticia import NoticiaRaspadaUpdateSchema
from backend.resources.notice.noticia_service import NoticiaService
from backend.resources.notice_message_devolute.notice_message_devolute_schema import NoticiaRaspadaMsgCreateSchema
from backend.resources.notice_message_devolute.notice_message_devolute_service import NoticiaRaspadaMsgService
from backend.resources.notice_name.noticia_nome import NoticiaRaspadaNomeCreateSchema
from backend.resources.user.user_service import UserService
from backend.resources.notice_name.noticia_nome_service import NoticiaNomeService
from view_components.middleware.check_auth import require_authentication
from view_components.components.shared.navsidebar import navsidebar

session = SessionLocal()
user_service = UserService(session)
noticia_service = NoticiaService(session)
noticia_raspada_msg_service = NoticiaRaspadaMsgService(session)
noticia_nome_service = NoticiaNomeService(session)

def load_css():
    css = """
        <style>
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
                line-height: 1.2;
                font-size: 0.9rem;
            }
            /* Outros ajustes */
            /* ... resto do CSS ... */
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)


@require_authentication
def main(current_user=None):
    st.set_page_config(page_title="Aprovar Notícias", layout="wide")
    load_css()
    navsidebar(current_user)

    users = user_service.find_all()
    user_options = ["-"] + [user.USERNAME for user in users]

    if 'selected_period' not in st.session_state:
        st.session_state['selected_period'] = "-"
    if 'selected_user' not in st.session_state:
        st.session_state['selected_user'] = "-"
    if 'page' not in st.session_state:
        st.session_state['page'] = 1
    # Nova flag para controlar o fluxo de aprovação
    if 'approval_started' not in st.session_state:
        st.session_state['approval_started'] = False

    # Verifica se já existem notícias com status "00-START-APPROVE"
    noticias_editaveis, count_editaveis = noticia_service.listar_noticias(
        page=1, 
        per_page=1, 
        filters={'STATUS': ['00-START-APPROVE']}
    )
    print(count_editaveis)
    if count_editaveis > 0:
        st.session_state['approval_started'] = True
    else:
        st.session_state['approval_started'] = False

    with st.sidebar:
        selected_user = st.selectbox(
            "Usuário:",
            user_options,
            index=user_options.index(st.session_state['selected_user'])
                  if st.session_state['selected_user'] in user_options else 0,
            key='selected_user'
        )

    if st.session_state['selected_period'] != "-" or st.session_state['selected_user'] != "-":
        st.session_state['page'] = 1

    # Define o filtro de STATUS de acordo com o fluxo
    if st.session_state['approval_started']:
        print('if')
        filters = {'STATUS': ['00-START-APPROVE']}
    else:
        print('else')
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

    if noticias:
        # Exibe o botão de fluxo dependendo do status atual
        if not st.session_state['approval_started']:
            with st.container():
                if st.button("Iniciar Aprovação", key="start_approval", icon=":material/play_arrow:"):
                    with st.spinner("Iniciando aprovação..."):
                        for noticia in noticias:
                            update_data = NoticiaRaspadaUpdateSchema(STATUS='00-START-APPROVE')
                            noticia_service.atualizar_noticia(noticia.ID, update_data)
                    st.session_state['approval_started'] = True
                    st.toast("Aprovação iniciada!")
                    st.rerun()
        else:
            with st.container():
                col_taskbar = st.columns([6, 2])
                with col_taskbar[0]:
                    if st.button("Aprovar Todas as Notícias", key="approve_all", icon=":material/done_all:", type='primary'):
                        with st.spinner("Aprovando todas as notícias..."):
                            for noticia in noticias:
                                update_data = NoticiaRaspadaUpdateSchema(STATUS='201-APPROVED')
                                noticia_service.atualizar_noticia(noticia.ID, update_data)
                        st.toast("Todas as notícias foram aprovadas!")
                        st.rerun()
        st.divider()

    # Lista cada notícia com os inputs condicionais
    if noticias:
        for noticia in noticias:
            # Define se os inputs devem ser editáveis somente quando o status for 00-START-APPROVE
            is_editable = (noticia.STATUS == "00-START-APPROVE")
            with st.container():
                st.markdown(f"###### Data Publicação: {noticia.DATA_PUBLICACAO.strftime('%d/%m/%Y')}")
                if hasattr(noticia, 'URL'):
                    st.markdown(f"**URL:** {noticia.URL}")

                col_top1, col_top2, col_top3 = st.columns(3)
                with col_top1:
                    font = st.text_input("Fonte", value=noticia.FONTE, key=f"fonte_{noticia.ID}", disabled=not is_editable)
                with col_top2:
                    title = st.text_input("Título", value=noticia.TITULO, key=f"titulo_{noticia.ID}", disabled=not is_editable)
                with col_top3:
                    category = st.text_input("Categoria", value=noticia.CATEGORIA, key=f"categoria_{noticia.ID}", disabled=not is_editable)

                col_bottom1, col_bottom2, col_bottom3 = st.columns(3)
                with col_bottom1:
                    region = st.text_input("Região", value=noticia.REGIAO if noticia.REGIAO else "", key=f"regiao_{noticia.ID}", disabled=not is_editable)
                with col_bottom2:
                    uf_list = ['N/A', 'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
                               'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
                               'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
                    uf_value = noticia.UF if noticia.UF in uf_list else 'N/A'
                    uf = st.selectbox("UF", options=uf_list, index=uf_list.index(uf_value), key=f"uf_{noticia.ID}", disabled=not is_editable)
                with col_bottom3:
                    reg_noticia = noticia.REG_NOTICIA if noticia.REG_NOTICIA else ""
                    st.text_input("Número do Registro da Notícia (já existente)",
                                  value=reg_noticia if reg_noticia else 'NÃO PREENCHIDO',
                                  key=f"reg_noticia_{noticia.ID}",
                                  disabled=True)
                    if is_editable:
                        arquivo_up = st.file_uploader("SELECIONE O ARQUIVO", key=f"file_{noticia.ID}", label_visibility="hidden")
                        if arquivo_up is not None:
                            reg_noticia = os.path.splitext(arquivo_up.name)[0]
                        else:
                            reg_noticia = noticia.REG_NOTICIA if noticia.REG_NOTICIA else ""
                    else:
                        st.write(f"Arquivo: {reg_noticia if reg_noticia else 'Não definido'}")

            # Exibe os nomes raspados com opção de editar (caso existam)
            if noticia.nomes_raspados:
                headers = [
                    "Editar", "Nome", "CPF", "Apelido", "Nome/CPF", "Sexo", "Pessoa",
                    "Idade", "Aniversário", "Atividade", "Envolvimento", "Suspeita",
                    "P.Pública", "PPE", "Operação"
                ]
                weights = [2, 1, 1.5, 1.5, 1.5, 1, 1, 0.7, 1.2, 1.5, 2, 1.5, 1, 1, 1.5]
                header_cols = st.columns(weights)
                for col, header in zip(header_cols, headers):
                    col.markdown(f"<p style='text-align: center;'><strong>{header}</strong></p>", unsafe_allow_html=True)
                
                for nome_obj in noticia.nomes_raspados:
                    row_cols = st.columns(weights)
                    with row_cols[0]:
                        inner_cols = st.columns([1, 1, 1])
                        with inner_cols[1]:
                            if is_editable:
                                if st.button("", icon=":material/edit_square:", key=f"editar_nome_{nome_obj.ID}"):
                                    edit_nome_dialog(nome_obj, noticia.ID)
                            else:
                                st.button("", icon=":material/edit_square:", key=f"editar_nome_{nome_obj.ID}", disabled=True)
                    with row_cols[1]:
                        st.markdown(f"<p style='text-align: center;'>{nome_obj.NOME if nome_obj.NOME else '-'}</p>", unsafe_allow_html=True)
                    with row_cols[2]:
                        st.markdown(f"<p style='text-align: center;'>{nome_obj.CPF if nome_obj.CPF else '-'}</p>", unsafe_allow_html=True)
                    with row_cols[3]:
                        st.markdown(f"<p style='text-align: center;'>{nome_obj.APELIDO if nome_obj.APELIDO else '-'}</p>", unsafe_allow_html=True)
                    with row_cols[4]:
                        st.markdown(f"<p style='text-align: center;'>{nome_obj.NOME_CPF if nome_obj.NOME_CPF else '-'}</p>", unsafe_allow_html=True)
                    with row_cols[5]:
                        st.markdown(f"<p style='text-align: center;'>{nome_obj.SEXO if nome_obj.SEXO else '-'}</p>", unsafe_allow_html=True)
                    with row_cols[6]:
                        st.markdown(f"<p style='text-align: center;'>{nome_obj.PESSOA if nome_obj.PESSOA else '-'}</p>", unsafe_allow_html=True)
                    with row_cols[7]:
                        st.markdown(f"<p style='text-align: center;'>{nome_obj.IDADE if nome_obj.IDADE else '-'}</p>", unsafe_allow_html=True)
                    with row_cols[8]:
                        date_str = nome_obj.ANIVERSARIO.strftime("%d/%m/%Y") if nome_obj.ANIVERSARIO else ""
                        st.markdown(f"<p style='text-align: center;'>{date_str if date_str else '-'}</p>", unsafe_allow_html=True)
                    with row_cols[9]:
                        st.markdown(f"<p style='text-align: center;'>{nome_obj.ATIVIDADE if nome_obj.ATIVIDADE else '-'}</p>", unsafe_allow_html=True)
                    with row_cols[10]:
                        st.markdown(f"<p style='text-align: center;'>{nome_obj.ENVOLVIMENTO if nome_obj.ENVOLVIMENTO else '-'}</p>", unsafe_allow_html=True)
                    with row_cols[11]:
                        st.markdown(f"<p style='text-align: center;'>{nome_obj.TIPO_SUSPEITA if nome_obj.TIPO_SUSPEITA else '-'}</p>", unsafe_allow_html=True)
                    with row_cols[12]:
                        st.markdown(f"<p style='text-align: center;'>{'Positivo' if nome_obj.FLG_PESSOA_PUBLICA else 'Negativo'}</p>", unsafe_allow_html=True)
                    with row_cols[13]:
                        st.markdown(f"<p style='text-align: center;'>{'Positivo' if nome_obj.INDICADOR_PPE else 'Negativo'}</p>", unsafe_allow_html=True)
                    with row_cols[14]:
                        st.markdown(f"<p style='text-align: center;'>{nome_obj.OPERACAO if nome_obj.OPERACAO else '-'}</p>", unsafe_allow_html=True)
            else:
                st.write("Nenhum nome extraído.")

            # Botão para gravar as alterações – somente se editável
            if is_editable:
                if st.button('Gravar', use_container_width=True, key=f"salvar_{noticia.ID}"):
                    update_data = NoticiaRaspadaUpdateSchema(
                        FONTE=font,
                        TITULO=title,
                        CATEGORIA=category,
                        REGIAO=region,
                        UF=uf,
                        REG_NOTICIA=reg_noticia
                    )
                    try:
                        noticia_service.atualizar_noticia(noticia.ID, update_data)
                        st.toast("Notícia gravada com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao gravar a notícia: {e}")
            
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


@st.dialog("Editar Nome")
def edit_nome_dialog(nome_obj, noticia_id):
    st.markdown(f"### Editar Nome - ID: {nome_obj.ID}")
    updated_nome = st.text_input("Nome", value=nome_obj.NOME, key=f"nome_dialog_{nome_obj.ID}_nome")
    updated_cpf = st.text_input("CPF", value=nome_obj.CPF, key=f"nome_dialog_{nome_obj.ID}_cpf")
    updated_apelido = st.text_input("Apelido", value=nome_obj.APELIDO, key=f"nome_dialog_{nome_obj.ID}_apelido")
    updated_sexo = st.text_input("Sexo", value=nome_obj.SEXO, key=f"nome_dialog_{nome_obj.ID}_sexo")
    updated_pessoa = st.text_input("Pessoa", value=nome_obj.PESSOA, key=f"nome_dialog_{nome_obj.ID}_pessoa")
    updated_idade = st.number_input("Idade", value=nome_obj.IDADE if nome_obj.IDADE is not None else 0,
                                    key=f"nome_dialog_{nome_obj.ID}_idade", min_value=0)
    updated_atividade = st.text_input("Atividade", value=nome_obj.ATIVIDADE, key=f"nome_dialog_{nome_obj.ID}_atividade")
    updated_envolvimento = st.text_area("Envolvimento", value=nome_obj.ENVOLVIMENTO,
                                        key=f"nome_dialog_{nome_obj.ID}_envolvimento")
    updated_tipo_suspeita = st.text_input("Tipo de Suspeita", value=nome_obj.TIPO_SUSPEITA,
                                          key=f"nome_dialog_{nome_obj.ID}_tipo_suspeita")
    updated_flg_pessoa_publica = st.checkbox(
        "Pessoa Pública",
        value=True if nome_obj.FLG_PESSOA_PUBLICA in ["S", "True", "true"] else False,
        key=f"nome_dialog_{nome_obj.ID}_flg_pessoa_publica"
    )
    updated_indicador_ppe = st.checkbox(
        "Indicador PPE",
        value=True if nome_obj.INDICADOR_PPE in ["S", "True", "true"] else False,
        key=f"nome_dialog_{nome_obj.ID}_indicador_ppe"
    )
    default_date = nome_obj.ANIVERSARIO if nome_obj.ANIVERSARIO is not None else datetime.date.today()
    updated_aniversario = st.date_input("Aniversário", value=default_date,
                                         key=f"nome_dialog_{nome_obj.ID}_aniversario")
    
    if st.button("Salvar Alterações"):
        data = NoticiaRaspadaNomeCreateSchema(
            CPF=st.session_state.get(f"nome_dialog_{nome_obj.ID}_cpf", nome_obj.CPF),
            NOME=st.session_state.get(f"nome_dialog_{nome_obj.ID}_nome", nome_obj.NOME),
            APELIDO=st.session_state.get(f"nome_dialog_{nome_obj.ID}_apelido", nome_obj.APELIDO),
            NOME_CPF=st.session_state.get(f"nome_dialog_{nome_obj.ID}_nome_cpf", 
                                          nome_obj.NOME_CPF if hasattr(nome_obj, "NOME_CPF") else None),
            SEXO=st.session_state.get(f"nome_dialog_{nome_obj.ID}_sexo", nome_obj.SEXO),
            PESSOA=st.session_state.get(f"nome_dialog_{nome_obj.ID}_pessoa", nome_obj.PESSOA),
            IDADE=st.session_state.get(f"nome_dialog_{nome_obj.ID}_idade", nome_obj.IDADE),
            ANIVERSARIO=st.session_state.get(f"nome_dialog_{nome_obj.ID}_aniversario", nome_obj.ANIVERSARIO),
            ATIVIDADE=st.session_state.get(f"nome_dialog_{nome_obj.ID}_atividade", nome_obj.ATIVIDADE),
            ENVOLVIMENTO=st.session_state.get(f"nome_dialog_{nome_obj.ID}_envolvimento", nome_obj.ENVOLVIMENTO),
            OPERACAO=nome_obj.OPERACAO,
            FLG_PESSOA_PUBLICA="S" if st.session_state.get(f"nome_dialog_{nome_obj.ID}_flg_pessoa_publica", False) else "N",
            ENVOLVIMENTO_GOV=None,
            INDICADOR_PPE="S" if st.session_state.get(f"nome_dialog_{nome_obj.ID}_indicador_ppe", False) else "N",
            NOTICIA_ID=noticia_id
        )
        try:
            noticia_nome_service.update(nome_obj.ID, data)
            st.toast("Nome atualizado com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao atualizar nome ID {nome_obj.ID}: {e}")


if __name__ == "__main__":
    main()
