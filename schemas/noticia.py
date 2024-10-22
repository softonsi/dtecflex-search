from datetime import datetime
from typing import Optional

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

class NoticiaRaspadaCreateSchema(NoticiaRaspadaBaseSchema):
    pass

class NoticiaRaspadaUpdateSchema(BaseModel):
    LINK_ID: Optional[str] = Field(None, max_length=64)
    URL: Optional[str] = Field(None, max_length=1000)
    FONTE: Optional[str] = Field(None, max_length=250)
    DATA_PUBLICACAO: Optional[datetime] = None
    CATEGORIA: Optional[str] = Field(None, max_length=50)
    QUERY: Optional[str] = Field(None, max_length=250)
    ID_ORIGINAL: Optional[str] = Field(None, max_length=2000)
    DT_RASPAGEM: Optional[datetime] = None
    DT_DECODE: Optional[datetime] = None
    TITULO: Optional[str] = Field(None, max_length=250)
    ID_USUARIO: Optional[int] = None
    STATUS: Optional[str] = Field(None, max_length=25)
    TEXTO_NOTICIA: Optional[str] = None
    LINK_ORIGINAL: Optional[str] = Field(None, max_length=2000)

    model_config = ConfigDict(from_attributes=True)

class NoticiaRaspadaSchema(NoticiaRaspadaBaseSchema):
    ID: int

    model_config = ConfigDict(from_attributes=True)
