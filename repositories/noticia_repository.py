from typing import List, Optional

from sqlalchemy.orm import Session

from models.database import NoticiaRaspadaModel
from schemas.noticia import NoticiaRaspadaCreateSchema, NoticiaRaspadaUpdateSchema


class NoticiaRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, noticia_data: NoticiaRaspadaCreateSchema) -> NoticiaRaspadaModel:
        #noticia = NoticiaRaspadaModel(**noticia_data.dict(exclude_unset=True))
        noticia = NoticiaRaspadaModel(**noticia_data.model_dump())
        self.session.add(noticia)
        self.session.commit()
        self.session.refresh(noticia)
        return noticia

    def get_by_id(self, noticia_id: int) -> Optional[NoticiaRaspadaModel]:
        return self.session.query(NoticiaRaspadaModel).filter(NoticiaRaspadaModel.ID == noticia_id).first()

    def xlist(self, limit: int = None) -> List[NoticiaRaspadaModel]:
        query = self.session.query(NoticiaRaspadaModel).order_by(NoticiaRaspadaModel.ID.desc())
        if limit:
            query = query.limit(limit)
        
        return query.all()

    def list(self, offset: int = 0, limit: int = 10) -> List[NoticiaRaspadaModel]:
        query = self.session.query(NoticiaRaspadaModel).order_by(NoticiaRaspadaModel.ID.desc())
        query = query.offset(offset).limit(limit)
        return query.all()

    def update(self, noticia_id: int, noticia_data: NoticiaRaspadaUpdateSchema) -> Optional[NoticiaRaspadaModel]:
        noticia = self.get_by_id(noticia_id)
        if noticia:
            for key, value in noticia_data.dict(exclude_unset=True).items():
                setattr(noticia, key, value)
            self.session.commit()
            self.session.refresh(noticia)
        return noticia

    def delete(self, noticia_id: int) -> bool:
        noticia = self.get_by_id(noticia_id)
        if noticia:
            self.session.delete(noticia)
            self.session.commit()
            return True
        return False
   
    def count(self) -> int:
            return self.session.query(NoticiaRaspadaModel).count()