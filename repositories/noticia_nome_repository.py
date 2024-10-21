from schemas.noticia_nome import NoticiaRaspadaNomeCreateSchema
from sqlalchemy.orm import Session, joinedload
from models.database import NoticiaRaspadaNomeModel
from datetime import datetime

class NoticiaNomeRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, noticia_data: NoticiaRaspadaNomeCreateSchema) -> NoticiaRaspadaNomeModel:
        #noticia = NoticiaRaspadaModel(**noticia_data.dict(exclude_unset=True))
        noticia = NoticiaRaspadaNomeModel(**noticia_data.model_dump())
        self.session.add(noticia)
        self.session.commit()
        self.session.refresh(noticia)
        return noticia

    def find_by_noticia_id(self, noticia_id):
        return self.session.query(NoticiaRaspadaNomeModel).options(
            joinedload(NoticiaRaspadaNomeModel.noticia)
        ).filter(NoticiaRaspadaNomeModel.NOTICIA_ID == noticia_id).all()
