from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, func
from sqlalchemy.orm import relationship
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
    # UF = Column(String(250), nullable=True)
    # REGIAO = Column(String(250), nullable=True)
    ID_ORIGINAL = Column(String(2000), nullable=False)
    DT_RASPAGEM = Column(DateTime, nullable=False, server_default=func.now())
    DT_DECODE = Column(DateTime, nullable=True)
    TITULO = Column(String(250), nullable=True)
    ID_USUARIO = Column(Integer, nullable=True)
    STATUS = Column(String(25), nullable=True)
    TEXTO_NOTICIA = Column(Text, nullable=True)
    LINK_ORIGINAL = Column(String(2000), nullable=True)

    nomes_raspados = relationship("NoticiaRaspadaNomeModel", back_populates="noticia")

    def __repr__(self):
        return f"<NoticiaRaspadaModel(ID={self.ID}, TITULO='{self.TITULO}')>"


class NoticiaRaspadaNomeModel(Base):
    __tablename__ = 'TB_NOTICIA_RASPADA_NOME2'

    ID = Column(Integer, primary_key=True, index=True)
    NOME = Column(String(2000), nullable=True)
    CPF = Column(String(15), nullable=True)
    NOME_CPF = Column(String(15), nullable=True)
    APELIDO = Column(String(100), nullable=True)
    SEXO = Column(String(100), nullable=True)
    PESSOA = Column(String(100), nullable=True)
    IDADE = Column(Integer, nullable=True)
    ATIVIDADE = Column(String(100), nullable=True)
    ENVOLVIMENTO = Column(String(100), nullable=True)
    TIPO_SUSPEITA = Column(String(100), nullable=True)
    FLG_PESSOA_PUBLICA = Column(String(100), nullable=True)
    ANIVERSARIO = Column(DateTime, nullable=True)
    INDICADOR_PP = Column(String(1), nullable=True)

    NOTICIA_ID = Column(Integer, ForeignKey('TB_NOTICIA_RASPADA.ID'), nullable=False)

    noticia = relationship("NoticiaRaspadaModel", back_populates="nomes_raspados")

    def __repr__(self):
        return f"<NoticiaRaspadaNomeModel(ID={self.ID}, NOME='{self.NOME}')>"
