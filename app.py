from datetime import date, datetime

import streamlit as st

from database import Base, SessionLocal, engine
from models.database import NoticiaRaspadaModel
from repositories.noticia_repository import NoticiaRepository
from schemas.noticia import (
    NoticiaRaspadaCreateSchema,
    NoticiaRaspadaSchema,
    NoticiaRaspadaUpdateSchema,
)
from services.noticia_service import NoticiaService

# Criando as tabelas no banco de dados (se ainda não existirem)
Base.metadata.create_all(bind=engine)

# Função principal da aplicação
def main():
    st.title("Lista de Notícias")

    # Criando a sessão do banco de dados
    session = SessionLocal()

    # Inicializando o repositório e o serviço
    noticia_repository = NoticiaRepository(session)
    noticia_service = NoticiaService(noticia_repository)

    # Estado para controlar edição
    if 'edit_mode' not in st.session_state:
        st.session_state['edit_mode'] = False
    if 'edit_id' not in st.session_state:
        st.session_state['edit_id'] = None

    # Função para listar as notícias
    # Permitir que o usuário escolha o número de notícias a exibir
    def listar_noticias():
        per_page = st.sidebar.number_input("Notícias por página", min_value=1, max_value=100, value=10)

        if 'page_number' not in st.session_state:
            st.session_state['page_number'] = 1

        total_noticias = noticia_repository.count()
        total_pages = (total_noticias + per_page - 1) // per_page

        st.write(f"Página {st.session_state['page_number']} de {total_pages}")
        cols = st.columns(3)
        with cols[0]:
            if st.button("Anterior", disabled=st.session_state['page_number'] <= 1):
                st.session_state['page_number'] -= 1
                st.rerun()
        with cols[2]:
            if st.button("Próxima", disabled=st.session_state['page_number'] >= total_pages):
                st.session_state['page_number'] += 1
                st.rerun()

        noticias = noticia_service.listar_noticias(page=st.session_state['page_number'], per_page=per_page)
        if noticias:
            noticias_data = [noticia.model_dump() for noticia in noticias]
            campos = list(noticias_data[0].keys())
            campos.extend(["Editar", "Excluir"])

            header_cols = st.columns(len(campos))
            for i, campo in enumerate(campos):
                header_cols[i].write(f"**{campo}**")

            for noticia in noticias_data:
                cols = st.columns(len(campos))
                for i, (campo, valor) in enumerate(noticia.items()):
                    cols[i].write(valor)

                with cols[-2]:
                    if st.button("Editar", key=f"edit_{noticia['ID']}_{st.session_state['page_number']}"):
                        st.session_state['edit_mode'] = True
                        st.session_state['edit_id'] = noticia['ID']
                        st.rerun()

                with cols[-1]:
                    if st.button("Excluir", key=f"delete_{noticia['ID']}_{st.session_state['page_number']}"):
                        noticia_service.deletar_noticia(noticia['ID'])
                        st.success(f"Notícia ID {noticia['ID']} excluída com sucesso.")
                        st.rerun()
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
                    st.success("Notícia atualizada com sucesso.")
                    st.session_state['edit_mode'] = False
                    st.session_state['edit_id'] = None
                    st.rerun()
                if submit_button2:
                    st.session_state['edit_mode'] = False
                    st.session_state['edit_id'] = None
                    st.rerun()
        else:
            st.error("Notícia não encontrada.")


    # Controle de fluxo entre listagem e edição
    if st.session_state['edit_mode'] and st.session_state['edit_id']:
        editar_noticia(st.session_state['edit_id'])
    else:
        listar_noticias()

    # Fechando a sessão do banco de dados
    session.close()

if __name__ == "__main__":
    main()
