import os
import jwt
from datetime import datetime, timedelta
from argon2 import PasswordHasher
from backend.resources.user.user_service import UserService
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

class AuthService:

    def __init__(self, user_service: UserService = UserService(), ph: PasswordHasher = PasswordHasher()):
        self.user_service = user_service
        self.ph = ph
        
    def login(self, username, password):
        user = self._find_by_username(username)

        verify_pwd = self._decode_password(password, user.senha)

        if not verify_pwd:
            return 'Invalid username or password'
        
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.admin,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }

        return self._generate_jwt_token(payload)

    def verify_token(self, token):
        return self._decode_jwt(token)

    def _find_by_username(self, username):
        try:
            return self.user_service.get_by_username(username)
        except Exception as e:
            raise Exception(f"Erro ao buscar usuário: {str(e)}")

    def _decode_password(self, input_password, hashed_password):
        return self.ph.verify(hashed_password, input_password)
    
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