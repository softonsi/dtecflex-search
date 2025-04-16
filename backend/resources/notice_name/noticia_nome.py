from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

class NoticiaRaspadaBaseSchema(BaseModel):
    LINK_ID: str = Field(..., max_length=64)
    URL: Optional[str] = Field(..., max_length=1000)
    FONTE: str = Field(..., max_length=250)
    DATA_PUBLICACAO: Optional[datetime] = None
    CATEGORIA: str = Field(..., max_length=50)
    QUERY: Optional[str] = Field(None, max_length=250)
    ID_ORIGINAL: str = Field(..., max_length=2000)
    DT_RASPAGEM: Optional[datetime] = None
    DT_DECODE: Optional[datetime] = None
    TITULO: Optional[str] = Field(None, max_length=250)
    ID_USUARIO: Optional[int] = None
    STATUS: Optional[str] = Field(None, max_length=25)
    TEXTO_NOTICIA: Optional[str] = None
    LINK_ORIGINAL: Optional[str] = Field(None, max_length=2000)

    model_config = ConfigDict(from_attributes=True)

class NoticiaRaspadaNomeCreateSchema(BaseModel):
    NOME: Optional[str] = Field(None, max_length=2000)
    OPERACAO: Optional[str] = Field(None, max_length=50)
    CPF: Optional[str] = Field(None, max_length=15)
    NOME_CPF: Optional[str] = Field(None, max_length=200)
    APELIDO: Optional[str] = Field(None, max_length=100)
    SEXO: Optional[str] = Field(None, max_length=100)
    PESSOA: Optional[str] = Field(None, max_length=100)
    IDADE: Optional[int] = None
    ATIVIDADE: Optional[str] = Field(None, max_length=100)
    ENVOLVIMENTO: Optional[str] = Field(None, max_length=100)
    TIPO_SUSPEITA: Optional[str] = Field(None, max_length=100)
    # FLG_PESSOA_PUBLICA: Optional[str] = Field(None, max_length=100)
    FLG_PESSOA_PUBLICA: bool = False
    ANIVERSARIO: Optional[datetime] = None
    INDICADOR_PPE: bool = False
    NOTICIA_ID: int
# Esquema de criação que inclui os nomes
class NoticiaRaspadaCreateSchema(NoticiaRaspadaBaseSchema):
    NOMES_RASPADOS: Optional[List[NoticiaRaspadaNomeCreateSchema]] = []

    model_config = ConfigDict(from_attributes=True)

class NoticiaRaspadaNomeByNoticiaId(BaseModel):
    NOTICIA_ID: int
