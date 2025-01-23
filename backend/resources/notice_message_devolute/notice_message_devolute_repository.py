from sqlalchemy.orm import Session
from backend.models.database import NoticiaRaspadaMsgModel
from datetime import date

class NoticiaRaspadaMsgRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_msg(self, noticia_id: int, msg_text: str, user_id: int) -> NoticiaRaspadaMsgModel:
        new_msg = NoticiaRaspadaMsgModel(
            NOTICIA_ID=noticia_id,
            MSG_TEXT=msg_text,
            MSG_STATUS='',
            MSG_TIME=date.today(),
            ID_USUARIO=user_id
        )
        self.db_session.add(new_msg)
        self.db_session.commit()
        self.db_session.refresh(new_msg)
        return new_msg

    def get_msg_by_noticia_id(self, noticia_id: int) -> list[NoticiaRaspadaMsgModel]:
        return self.db_session.query(NoticiaRaspadaMsgModel).filter(NoticiaRaspadaMsgModel.NOTICIA_ID == noticia_id).all()
