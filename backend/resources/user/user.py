from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreateBaseSchema(BaseModel):
    username: str = Field(..., max_length=50, description="Nome de usuário único")
    # email: str = Field(..., max_length=120, description="Endereço de e-mail válido")
    senha: str = Field(..., min_length=8, max_length=128, description="Senha segura")
    admin: Optional[bool] = Field(None, description="Indica se o usuário tem privilégios de administrador")
    
    class Config:
        orm_mode = True