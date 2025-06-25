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

    @property
    def full_participants(self) -> list[str]:
        return list(dict.fromkeys(self.participants + [self.host_email]))  # host까지 포함한 전체 참가자 이메일 리스트

    class Config:
        extra = "ignore"

