from sqlalchemy.orm import Session

from backend.models.database import NoticiaRaspadaMsgModel
from backend.resources.notice_message_devolute.notice_message_devolute_repository import NoticiaRaspadaMsgRepository
from backend.resources.notice_message_devolute.notice_message_devolute_schema import NoticiaRaspadaMsgCreateSchema

class NoticiaRaspadaMsgService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.repository = NoticiaRaspadaMsgRepository(db_session)

    def create_msg(self, noticia_id: int, msg_data: NoticiaRaspadaMsgCreateSchema, user_id: int) -> NoticiaRaspadaMsgModel:
        return self.repository.create_msg(
            noticia_id=noticia_id,
            msg_text=msg_data.MSG_TEXT,
            user_id=user_id
        )

    def get_msgs_by_noticia_id(self, noticia_id: int) -> list[NoticiaRaspadaMsgModel]:
        return self.repository.get_msg_by_noticia_id(noticia_id)
