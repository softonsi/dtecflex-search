from typing import Optional

from backend.resources.notice_name.noticia_nome_repository import NoticiaNomeRepository
from database import SessionLocal
from backend.resources.notice_name.noticia_nome import NoticiaRaspadaNomeCreateSchema
session = SessionLocal()

class NoticiaNomeService:
    def __init__(self, noticia_name_repository: NoticiaNomeRepository = NoticiaNomeRepository(session)):
        self.noticia_nome_repository = noticia_name_repository

    def create(self, noticia_nome_data: NoticiaRaspadaNomeCreateSchema) -> NoticiaRaspadaNomeCreateSchema:
        noticia = self.noticia_nome_repository.create(noticia_nome_data)
        return NoticiaRaspadaNomeCreateSchema.model_validate(noticia, from_attributes=True)

    def find_noticia_nome_by_noticia_id(self, noticia_id):
        return self.noticia_nome_repository.find_by_noticia_id(noticia_id)

    def update(self, nome_id: int, data: NoticiaRaspadaNomeCreateSchema) -> Optional[NoticiaRaspadaNomeCreateSchema]:
        return self.noticia_nome_repository.update(nome_id, data)

    def delete(self, nome_id: int) -> bool:
        return self.noticia_nome_repository.delete(nome_id)
