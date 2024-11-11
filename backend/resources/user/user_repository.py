from pymysql import IntegrityError
from database import SessionLocal
from sqlalchemy.orm import Session

from backend.models.database import UsuarioModel

session = SessionLocal()

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data):
        try:
            self.session.add(data)
            self.session.commit()
            self.session.refresh(data)
            return data
        except IntegrityError as e:
            self.session.rollback()
            if 'unique constraint' in str(e.orig).lower():
                raise ValueError("Email ou nome de usuário já estão em uso.")
            else:
                raise Exception("Erro ao criar usuário.")
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Erro inesperado: {str(e)}")
        
    def get_by_username(self, username):
        try:
            return self.session.query(UsuarioModel).filter(UsuarioModel.USERNAME == username).first()
        except Exception as e:
            raise Exception(f"Erro ao buscar usuário: {str(e)}")