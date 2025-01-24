import streamlit as st
from database import  SessionLocal
from backend.resources.notice.noticia_repository import NoticiaRepository

st.title('teste')

session = SessionLocal()

noticia_repository = NoticiaRepository(session)

# Supondo que o ID do usuário seja 1 e que você queira trazer 10 notícias com paginação
usuario_id = 5
noticias = noticia_repository.listar_noticias_edit_mode_por_usuario(usuario_id, offset=0, limit=10)
print(noticias)
# Exibindo as notícias e suas mensagens
# for noticia in noticias:
#     print(f"Notícia: {noticia.TITULO}")
#     if noticia.mensagens:  # Verificando se a notícia tem mensagens associadas
#         for mensagem in noticia.mensagens:
#             print(f"Mensagem: {mensagem.MSG_TEXT}")