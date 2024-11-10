from argon2 import PasswordHasher
from database import SessionLocal
from backend.models.database import UsuarioModel
from backend.resources.user.user_repository import UserRepository
from backend.resources.user.user import UserCreateBaseSchema

session = SessionLocal()

class UserService:

    def __init__(self, user_repository: UserRepository = UserRepository(session)):
        self.user_repository = user_repository

    def get_by_username(self, username):
        return self.user_repository.get_by_username(username)

    def create(self, username: str, pwd:str, admin: bool=False) -> UsuarioModel:
        try:
            user_data = UserCreateBaseSchema(
                username=username,
                senha=pwd,
                admin=admin or False
            )

            new_user = UsuarioModel(
                username=user_data.username,
                email=user_data.email,
                hashed_password=self._hash_password(user_data.senha),
                admin=user_data.admin or False
            )

            return self.user_repository.create(new_user)

        except Exception as e:
            raise ValueError(f"Dados inválidos: {str(e)}")

    def _hash_password(self, password: str) -> str:
        ph = PasswordHasher()
        return ph.hash(password)