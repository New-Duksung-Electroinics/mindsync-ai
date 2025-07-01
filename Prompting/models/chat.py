from pydantic import BaseModel
from datetime import datetime


class ChatMessage(BaseModel):
    """
    ChatMessage: 개별 채팅 메세지 데이터 구조.
    """
    name: str
    email: str
    message: str
    agendaId: str
    timestamp: datetime

    class Config:
        extra = "ignore"


class RoomMessages(BaseModel):
    """
    RoomMessages: 특정 채팅방의 메시지를 안건 ID별로 나눈 데이터 구조.

    - _id: 채팅방 ID(uuid 형식)
    - messages: {agenda_id: [ChatMessage, ...], }
    """
    _id: str
    messages: dict[str, list[ChatMessage]]   # 안건 ID(aid) - 안건에 대한 채팅 내역

    class Config:
        extra = "ignore"

