from pymysql import IntegrityError
from sqlalchemy.orm import Session
from backend.models.database import UsuarioModel

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: UsuarioModel):
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
        
    def find_all(self):
        try:
            return self.session.query(UsuarioModel).all()
        except Exception as e:
            raise Exception(f"Erro ao buscar todos os usuários: {str(e)}")
    
    def get_by_username(self, username: str):
        try:
            return self.session.query(UsuarioModel).filter(UsuarioModel.USERNAME == username).first()
        except Exception as e:
            raise Exception(f"Erro ao buscar usuário: {str(e)}")

    def get_by_id(self, user_id: int):
        try:
            return self.session.query(UsuarioModel).filter(UsuarioModel.ID == user_id).first()
        except Exception as e:
            raise Exception(f"Erro ao buscar usuário: {str(e)}")

    def update(self, user: UsuarioModel):
        try:
            self.session.commit()
            self.session.refresh(user)
            return user
        except IntegrityError as e:
            self.session.rollback()
            if 'unique constraint' in str(e.orig).lower():
                raise ValueError("Email ou nome de usuário já estão em uso.")
            else:
                raise Exception("Erro ao atualizar usuário.")
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Erro inesperado: {str(e)}")
        
    def delete(self, user: UsuarioModel):
        try:
            self.session.delete(user)
            self.session.commit()
            return user
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Erro ao excluir usuário: {str(e)}")
