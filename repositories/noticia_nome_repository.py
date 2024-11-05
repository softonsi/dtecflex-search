from typing_extensions import Optional
from schemas.noticia_nome import NoticiaRaspadaNomeCreateSchema
from sqlalchemy.orm import Session, joinedload
from models.database import NoticiaRaspadaNomeModel
from datetime import datetime

class NoticiaNomeRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, noticia_data: NoticiaRaspadaNomeCreateSchema) -> NoticiaRaspadaNomeModel:
        noticia = NoticiaRaspadaNomeModel(**noticia_data.model_dump())
        self.session.add(noticia)
        self.session.commit()
        self.session.refresh(noticia)
        return noticia

    def find_by_noticia_id(self, noticia_id):
        return self.session.query(NoticiaRaspadaNomeModel).options(
            joinedload(NoticiaRaspadaNomeModel.noticia)
        ).filter(NoticiaRaspadaNomeModel.NOTICIA_ID == noticia_id).all()

    def update(self, nome_id: int, data: NoticiaRaspadaNomeCreateSchema) -> Optional[NoticiaRaspadaNomeModel]:
        nome = self.get_by_id(nome_id)
        if nome:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(nome, key, value)
            try:
                self.session.commit()
                self.session.refresh(nome)
                return nome
            except Exception as e:
                self.session.rollback()
                print(f"Erro ao atualizar o nome: {e}")
                return None
        return None

    def get_by_id(self, nome_id: int) -> Optional[NoticiaRaspadaNomeModel]:
            return self.session.query(NoticiaRaspadaNomeModel).filter_by(ID=nome_id).first()

    def delete(self, nome_id: int) -> bool:
            nome = self.get_by_id(nome_id)
            if nome:
                try:
                    self.session.delete(nome)
                    self.session.commit()
                    return True
                except Exception as e:
                    self.session.rollback()
                    print(f"Erro ao deletar o nome: {e}")
                    return False
            return False
