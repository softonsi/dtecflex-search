from database import Base, SessionLocal, engine
from repositories.noticia_repository import NoticiaRepository
from schemas.noticia import NoticiaRaspadaCreateSchema
from services.noticia_service import NoticiaService

# Criando as tabelas no banco de dados (se ainda não existirem)
# Base.metadata.create_all(bind=engine)

def main():
    session = SessionLocal()
    noticia_repository = NoticiaRepository(session)
    print(noticia_repository)
    noticia_service = NoticiaService(noticia_repository)
    print(noticia_service)
    
    noticias_testes = [
        NoticiaRaspadaCreateSchema(
            LINK_ID="link1",
            URL="http://exemplo.com/noticia/1",
            FONTE="Fonte A",
            CATEGORIA="Categoria A",
            ID_ORIGINAL="id_original_1",
            TITULO="Título 1",
            STATUS="Nova",
            QUERY="Teste Query 1",
        ),
        NoticiaRaspadaCreateSchema(
            LINK_ID="link2",
            URL="http://exemplo.com/noticia/2",
            FONTE="Fonte B",
            CATEGORIA="Categoria B",
            ID_ORIGINAL="id_original_2",
            TITULO="Título 2",
            STATUS="Nova",
            QUERY="Teste Query 2",
        ),
    ]

    for noticia_data in noticias_testes:
        noticia_service.criar_noticia(noticia_data)

    print("Notícias de teste inseridas com sucesso.")

    session.close()

if __name__ == "__main__":
    main()
