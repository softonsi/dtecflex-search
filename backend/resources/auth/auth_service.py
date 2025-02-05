import os
import jwt
from datetime import datetime, timedelta
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from backend.exceptions.auth_exceptions import AuthenticationError
from backend.resources.user.user_service import UserService
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

class AuthService:

    def __init__(self, session, user_service_cls=UserService, ph: PasswordHasher = PasswordHasher()):
        self.user_service = user_service_cls(session)
        self.ph = ph
        
    def login(self, username, password):
        try:
            user = self._find_by_username(username)
            if not self._decode_password(password, user.SENHA):
                raise AuthenticationError("Usuário ou senha inválidos")
            payload = {
                'user_id': user.ID,
                'username': user.USERNAME,
                'admin': user.ADMIN,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }
            return self._generate_jwt_token(payload)
        except Exception as e:
            raise e
        
    def verify_token(self, token):
        return self._decode_jwt(token)

    def decode_jwt(self, token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            print("O token expirou.")
            return None
        except jwt.InvalidTokenError:
            print("Token inválido.")
            return None
    
    def _find_by_username(self, username):
        try:
            return self.user_service.get_by_username(username)
        except Exception as e:
            raise Exception(f"Erro ao buscar usuário: {str(e)}")

    def _decode_password(self, input_password, hashed_password):
        try:
            return self.ph.verify(hashed_password, input_password)
        except VerifyMismatchError:
            return False
    
    def _generate_jwt_token(self, payload):
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    def _decode_jwt(token):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            print("O token expirou.")
            return None
        except jwt.InvalidTokenError:
            print("Token inválido.")
            return None