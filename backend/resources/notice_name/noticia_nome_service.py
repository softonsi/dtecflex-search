from typing import List, Optional
from backend.models.database import NoticiaRaspadaNomeModel
from backend.resources.notice_name.noticia_nome_repository import NoticiaNomeRepository
from backend.resources.notice_name.noticia_nome import NoticiaRaspadaNomeCreateSchema

class NoticiaNomeService:
    def __init__(self, session, noticia_name_repository_cls=NoticiaNomeRepository):
        self.noticia_nome_repository = noticia_name_repository_cls(session)

    def create(self, noticia_nome_data: NoticiaRaspadaNomeCreateSchema) -> NoticiaRaspadaNomeCreateSchema:
        noticia = self.noticia_nome_repository.create(noticia_nome_data)
        return NoticiaRaspadaNomeCreateSchema.model_validate(noticia, from_attributes=True)
    
    def listar_nomes_por_status_e_data_hoje(self, status) -> List[NoticiaRaspadaNomeModel]:
        return self.noticia_nome_repository.listar_nomes_por_status_e_data_hoje(status)
    
    def obter_contagem_por_status(self) -> List[NoticiaRaspadaNomeModel]:
        return self.noticia_nome_repository.obter_contagem_por_status()

    def find_noticia_nome_by_noticia_id(self, noticia_id):
        return self.noticia_nome_repository.find_by_noticia_id(noticia_id)

    def update(self, nome_id: int, data: NoticiaRaspadaNomeCreateSchema) -> Optional[NoticiaRaspadaNomeCreateSchema]:
        return self.noticia_nome_repository.update(nome_id, data)

    def delete(self, nome_id: int) -> bool:
        return self.noticia_nome_repository.delete(nome_id)
