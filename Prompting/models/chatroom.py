from pydantic import BaseModel
from typing import Optional


class AgendaSummaryModel(BaseModel):
    agendaId: str
    topic: str
    content: Optional[str]


class RoomModel(BaseModel):
    # _id: str
    roomId: str
    host_email: str
    # title: str
    content: str
    participants: list[str]
    # mbti: str
    # summary: list[AgendaSummaryModel]

    class Config:
        extra = "ignore"

