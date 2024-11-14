from argon2 import PasswordHasher
from database import SessionLocal
from backend.models.database import UsuarioModel
from backend.resources.user.user_repository import UserRepository
from backend.resources.user.user_schema import UserCreateBaseSchema

session = SessionLocal()

class UserService:

    def __init__(self, user_repository: UserRepository = UserRepository(session)):
        self.user_repository = user_repository

    def get_by_username(self, username):
        return self.user_repository.get_by_username(username)
    
    def find_all(self):
        return self.user_repository.find_all()

    def create(self, username: str, pwd:str, admin: bool=False) -> UsuarioModel:
        try:
            user_data = UserCreateBaseSchema(
                USUARIO=username,
                SENHA=pwd,
                ADMIN=admin or False
            )

            new_user = UsuarioModel(
                USUARIO=user_data.USUARIO,
                # email=user_data.email,
                SENHA=self._hash_password(user_data.SENHA),
                ADMIN=user_data.ADMIN or False
            )

            return self.user_repository.create(new_user)

        except Exception as e:
            raise ValueError(f"Dados inválidos: {str(e)}")

    def _hash_password(self, password: str) -> str:
        ph = PasswordHasher()
        return ph.hash(password)