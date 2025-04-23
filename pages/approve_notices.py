import os
from datetime import date, datetime
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
    if 'approval_started' not in st.session_state:
        st.session_state['approval_started'] = False

    noticias_editaveis, count_editaveis = noticia_service.listar_noticias(
        page=1, 
        per_page=1, 
        filters={'STATUS': ['00-START-APPROVE']}
    )
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

    if st.session_state['approval_started']:
        filters = {'STATUS': ['00-START-APPROVE']}
    else:
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
            global_unsaved = False
            uf_list = ['N/A', 'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
                       'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
                       'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
            for noticia in noticias:
                current_font = st.session_state.get(f"fonte_{noticia.ID}", noticia.FONTE)
                current_title = st.session_state.get(f"titulo_{noticia.ID}", noticia.TITULO)
                current_category = st.session_state.get(f"categoria_{noticia.ID}", noticia.CATEGORIA)
                current_region = st.session_state.get(f"regiao_{noticia.ID}", noticia.REGIAO if noticia.REGIAO else "")
                current_uf = st.session_state.get(f"uf_{noticia.ID}", noticia.UF if noticia.UF in uf_list else "N/A")
                current_reg = st.session_state.get(f"reg_noticia_{noticia.ID}", noticia.REG_NOTICIA if noticia.REG_NOTICIA else "")
                if (current_font != noticia.FONTE or 
                    current_title != noticia.TITULO or 
                    current_category != noticia.CATEGORIA or 
                    current_region != (noticia.REGIAO if noticia.REGIAO else "") or 
                    current_uf != (noticia.UF if noticia.UF in uf_list else "N/A") or 
                    current_reg != (noticia.REG_NOTICIA if noticia.REG_NOTICIA else "")):
                    global_unsaved = True
                    break

            with st.container():
                col_taskbar = st.columns([6, 2])
                with col_taskbar[0]:
                    if st.button("Aprovar Todas as Notícias", 
                                 key="approve_all", 
                                 icon=":material/done_all:", 
                                 type='primary', 
                                 disabled=global_unsaved):
                        with st.spinner("Aprovando todas as notícias..."):
                            for noticia in noticias:
                                update_data = NoticiaRaspadaUpdateSchema(STATUS='201-APPROVED', DT_APROVACAO=datetime.now())
                                noticia_service.atualizar_noticia(noticia.ID, update_data)
                        st.toast("Todas as notícias foram aprovadas!")
                        st.rerun()
        st.divider()

    if noticias:
        for noticia in noticias:
            is_editable = (noticia.STATUS == "00-START-APPROVE")
            with st.container():
                st.markdown(f"###### Data Publicação: {noticia.DATA_PUBLICACAO.strftime('%d/%m/%Y')}")
                if hasattr(noticia, 'URL'):
                    st.markdown(f"**URL:** {noticia.URL}")

                # Inputs da notícia (não relacionados aos nomes)
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
                    reg_atual = noticia.REG_NOTICIA if noticia.REG_NOTICIA else ""
                    st.text_input("Número do Registro da Notícia (já existente)",
                                  value=reg_atual if reg_atual else 'NÃO PREENCHIDO',
                                  key=f"reg_noticia_display_{noticia.ID}",
                                  disabled=True)
                    if is_editable:
                        arquivo_up = st.file_uploader("SELECIONE O ARQUIVO", key=f"file_{noticia.ID}", label_visibility="hidden")
                        if arquivo_up is not None:
                            reg_noticia = os.path.splitext(arquivo_up.name)[0]
                        else:
                            reg_noticia = reg_atual
                    else:
                        st.write(f"Arquivo: {reg_atual if reg_atual else 'Não definido'}")
                        reg_noticia = reg_atual  # Garante que a variável seja definida

            original_font = noticia.FONTE
            original_title = noticia.TITULO
            original_category = noticia.CATEGORIA
            original_region = noticia.REGIAO if noticia.REGIAO else ""
            original_uf = uf_value
            original_reg_noticia = reg_atual

            is_modified = (
                font != original_font or 
                title != original_title or 
                category != original_category or 
                region != original_region or 
                uf != original_uf or 
                reg_noticia != original_reg_noticia
            )

            if is_editable:
                if st.button('Gravar', use_container_width=True, key=f"salvar_{noticia.ID}", disabled=not is_modified):
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
                        st.markdown(f"<p style='text-align: center;'>{'Sim' if nome_obj.FLG_PESSOA_PUBLICA else 'Não'}</p>", unsafe_allow_html=True)
                    with row_cols[13]:
                        st.markdown(f"<p style='text-align: center;'>{'Sim' if nome_obj.INDICADOR_PPE else 'Não'}</p>", unsafe_allow_html=True)
                    with row_cols[14]:
                        st.markdown(f"<p style='text-align: center;'>{nome_obj.OPERACAO if nome_obj.OPERACAO else '-'}</p>", unsafe_allow_html=True)
            else:
                st.write("Nenhum nome extraído.")

            st.divider()

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
    
    sexo_options = ["M", "F", "NA"]
    updated_sexo = st.selectbox(
        "Sexo",
        options=sexo_options,
        index=sexo_options.index(nome_obj.SEXO) if nome_obj.SEXO in sexo_options else sexo_options.index("NA"),
        key=f"nome_dialog_{nome_obj.ID}_sexo"
    )
    
    pessoa_options = ["PF", "PJ", "NA"]
    updated_pessoa = st.selectbox(
        "Pessoa",
        options=pessoa_options,
        index=pessoa_options.index(nome_obj.PESSOA) if nome_obj.PESSOA in pessoa_options else pessoa_options.index("NA"),
        key=f"nome_dialog_{nome_obj.ID}_pessoa"
    )
    
    updated_idade = st.number_input(
        "Idade", 
        value=nome_obj.IDADE if nome_obj.IDADE is not None else 0,
        key=f"nome_dialog_{nome_obj.ID}_idade", 
        min_value=0
    )
    updated_atividade = st.text_input("Atividade", value=nome_obj.ATIVIDADE, key=f"nome_dialog_{nome_obj.ID}_atividade")
    updated_envolvimento = st.text_area("Envolvimento", value=nome_obj.ENVOLVIMENTO,
                                        key=f"nome_dialog_{nome_obj.ID}_envolvimento")
    updated_tipo_suspeita = st.text_input("Tipo de Suspeita", value=nome_obj.TIPO_SUSPEITA,
                                          key=f"nome_dialog_{nome_obj.ID}_tipo_suspeita")
    
    updated_flg_pessoa_publica = st.toggle(
        "Pessoa Pública",
        value=True if nome_obj.FLG_PESSOA_PUBLICA in [True, "True", "true", "S", 1] else False,
        key=f"nome_dialog_{nome_obj.ID}_flg_pessoa_publica"
    )
    updated_indicador_ppe = st.toggle(
        "Indicador PPE",
        value=True if nome_obj.INDICADOR_PPE in [True, "True", "true", "S", 1] else False,
        key=f"nome_dialog_{nome_obj.ID}_indicador_ppe"
    )
    
    default_date = nome_obj.ANIVERSARIO if nome_obj.ANIVERSARIO else None
    updated_aniversario = st.date_input(
        "Aniversário", 
        value=default_date,
        key=f"nome_dialog_{nome_obj.ID}_aniversario"
    )
    
    if st.button("Salvar Alterações"):
        data = NoticiaRaspadaNomeCreateSchema(
            CPF=updated_cpf,
            NOME=updated_nome,
            APELIDO=updated_apelido,
            NOME_CPF=st.session_state.get(
                f"nome_dialog_{nome_obj.ID}_nome_cpf", 
                nome_obj.NOME_CPF if hasattr(nome_obj, "NOME_CPF") else None
            ),
            SEXO=None if updated_sexo == 'NA' else updated_sexo,
            PESSOA=None if updated_pessoa == 'NA' else updated_pessoa,
            IDADE=updated_idade,
            ANIVERSARIO=updated_aniversario,
            ATIVIDADE=updated_atividade,
            ENVOLVIMENTO=updated_envolvimento,
            OPERACAO=nome_obj.OPERACAO,
            FLG_PESSOA_PUBLICA=updated_flg_pessoa_publica,
            ENVOLVIMENTO_GOV=None,
            INDICADOR_PPE=updated_indicador_ppe,
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
