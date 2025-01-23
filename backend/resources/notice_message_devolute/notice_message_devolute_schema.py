from pydantic import BaseModel
from datetime import date
from typing import Optional

class NoticiaRaspadaMsgCreateSchema(BaseModel):
    MSG_TEXT: str
    MSG_STATUS: Optional[str] = None
    MSG_TIME: Optional[date] = date.today()