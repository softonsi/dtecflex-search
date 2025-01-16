from argon2 import PasswordHasher
from database import SessionLocal
from backend.models.database import UsuarioModel
from backend.resources.user.user_repository import UserRepository
from backend.resources.user.user_schema import UserCreateBaseSchema

class UserService:

    def __init__(self, session, user_repository_cls=UserRepository):
        self.user_repository = user_repository_cls(session)

    def get_by_username(self, username):
        return self.user_repository.get_by_username(username)
    
    def find_all(self):
        return self.user_repository.find_all()

    def create(self, username: str, pwd:str, admin: bool=False) -> UsuarioModel:
        try:
            user_data = UserCreateBaseSchema(
                USERNAME=username,
                SENHA=pwd,
                ADMIN=admin or False
            )

            new_user = UsuarioModel(
                USERNAME=user_data.USERNAME,
                SENHA=self._hash_password(user_data.SENHA),
                ADMIN=user_data.ADMIN or False
            )

            return self.user_repository.create(new_user)

        except Exception as e:
            raise ValueError(f"Dados inválidos: {str(e)}")

    def _hash_password(self, password: str) -> str:
        ph = PasswordHasher()
        return ph.hash(password)