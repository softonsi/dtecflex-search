from sqlalchemy import Column, DateTime, Integer, String, Text, func

from database import Base


class NoticiaRaspadaModel(Base):
    __tablename__ = 'TB_NOTICIA_RASPADA'

    ID = Column(Integer, primary_key=True, index=True)
    LINK_ID = Column(String(64), nullable=False, unique=True)
    URL = Column(String(1000), nullable=False)
    FONTE = Column(String(250), nullable=False)
    DATA_PUBLICACAO = Column(DateTime, nullable=True)
    CATEGORIA = Column(String(50), nullable=False)
    QUERY = Column(String(250), nullable=True)
    ID_ORIGINAL = Column(String(2000), nullable=False)
    DT_RASPAGEM = Column(DateTime, nullable=False, server_default=func.now())
    DT_DECODE = Column(DateTime, nullable=True)
    TITULO = Column(String(250), nullable=True)
    ID_USUARIO = Column(Integer, nullable=True)
    STATUS = Column(String(25), nullable=True)
    TEXTO_NOTICIA = Column(Text, nullable=True)
    LINK_ORIGINAL = Column(String(2000), nullable=True)

    def __repr__(self):
        return f"<NoticiaRaspadaModel(ID={self.ID}, TITULO='{self.TITULO}')>"
