from typing import Any, Dict, List, Optional

from backend.models.database import NoticiaRaspadaMsgModel
from backend.resources.notice.noticia_repository import NoticiaRepository
from backend.resources.notice.noticia import (
    NoticiaRaspadaCreateSchema,
    NoticiaRaspadaSchema,
    NoticiaRaspadaUpdateSchema,
)
class NoticiaService:
    def __init__(self, session, noticia_repository_cls=NoticiaRepository):
        self.noticia_repository = noticia_repository_cls(session)

    def get_all_fontes(self) -> List[str]:
        return self.noticia_repository.get_all_fontes()

    def criar_noticia(self, noticia_data: NoticiaRaspadaCreateSchema) -> NoticiaRaspadaSchema:
        noticia = self.noticia_repository.create(noticia_data)
        return NoticiaRaspadaSchema.model_validate(noticia, from_attributes=True)

    def obter_noticia(self, noticia_id: int) -> Optional[NoticiaRaspadaSchema]:
        noticia = self.noticia_repository.get_by_id(noticia_id)
        if noticia:
            return NoticiaRaspadaSchema.model_validate(noticia, from_attributes=True)
        return None

    def get_by_id_with_names(self, noticia_id: int) -> Optional[NoticiaRaspadaSchema]:
        noticia_model = self.noticia_repository.get_by_id_with_names(noticia_id)
        if not noticia_model:
            return None

        noticia_schema = NoticiaRaspadaSchema.model_validate(noticia_model)
        return noticia_schema.model_dump()

    def atualizar_noticia(self, noticia_id: int, noticia_data: NoticiaRaspadaUpdateSchema) -> Optional[NoticiaRaspadaSchema]:
        noticia = None
        try:
            noticia = self.noticia_repository.update(noticia_id, noticia_data)
        except Exception as e:
            print(e)

        if noticia:
            return NoticiaRaspadaSchema.model_validate(noticia, from_attributes=True)
        return None

    def deletar_noticia(self, noticia_id: int) -> bool:
        return self.noticia_repository.delete(noticia_id)

    def xlistar_noticias(self, page: int = 1, per_page: int = 10) -> List[NoticiaRaspadaSchema]:
        offset = (page - 1) * per_page
        noticias = self.noticia_repository.list(offset=offset, limit=per_page)
        return [
            NoticiaRaspadaSchema.model_validate(noticia, from_attributes=True)
            for noticia in noticias
        ]

    def listar_noticias(self, page: int = 1, per_page: int = 10, filters: Optional[Dict[str, Any]] = None) -> (List[NoticiaRaspadaSchema], int):
        offset = (page - 1) * per_page
        noticias, total_count = self.noticia_repository.list(offset=offset, limit=per_page, filters=filters)
        
        noticias_schemas = []
        for noticia in noticias:
            noticia_schema = NoticiaRaspadaSchema.model_validate(noticia, from_attributes=True)
            
            if noticia.mensagens:
                noticia_schema.mensagens = [
                    NoticiaRaspadaMsgModel(
                        ID=msg.ID,
                        MSG_TEXT=msg.MSG_TEXT,
                        MSG_STATUS=msg.MSG_STATUS,
                        MSG_TIME=msg.MSG_TIME,
                        ID_USUARIO=msg.ID_USUARIO
                    )
                    for msg in noticia.mensagens
                ]
            
            noticias_schemas.append(noticia_schema)
        
        return noticias_schemas, total_count