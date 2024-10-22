from typing import Any, Dict, List, Optional, Tuple

from repositories.noticia_nome_repository import NoticiaNomeRepository
from repositories.noticia_repository import NoticiaRepository
from schemas.noticia import (
    NoticiaRaspadaCreateSchema,
    NoticiaRaspadaSchema,
    NoticiaRaspadaUpdateSchema,
)
from schemas.noticia_nome import NoticiaRaspadaNomeCreateSchema


class NoticiaNomeService:
    def __init__(self, noticia_nome_repository: NoticiaNomeRepository):
        self.noticia_nome_repository = noticia_nome_repository

    def create(self, noticia_nome_data: NoticiaRaspadaNomeCreateSchema) -> NoticiaRaspadaNomeCreateSchema:
        noticia = self.noticia_nome_repository.create(noticia_nome_data)
        return NoticiaRaspadaNomeCreateSchema.model_validate(noticia, from_attributes=True)

    def find_noticia_nome_by_noticia_id(self, noticia_id):
        return self.noticia_nome_repository.find_by_noticia_id(noticia_id)

    def update(self, nome_id: int, data: NoticiaRaspadaNomeCreateSchema) -> Optional[NoticiaRaspadaNomeCreateSchema]:
        return self.noticia_nome_repository.update(nome_id, data)

    def delete(self, nome_id: int) -> bool:
        return self.noticia_nome_repository.delete(nome_id)
