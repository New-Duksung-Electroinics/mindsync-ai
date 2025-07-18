# use case에서 쓰이는 data class 정의 모음
from dataclasses import dataclass
from Prompting.models import ChatMessage, UserModel, AgendaItemModel


@dataclass
class UserInfo:
    email: str
    name: str
    mbti: str

    @classmethod
    def from_model(cls, model: UserModel) -> "UserInfo":
        return cls(
            email=model.email,
            name=model.username,
            mbti=model.usermbti
        )

@dataclass
class ChatLog:
    sender: str
    message: str
    agenda_id: str

    @classmethod
    def from_model(cls, model: ChatMessage) -> "ChatLog":
        return cls(
            sender=model.email,
            message=model.message,
            agenda_id=model.agendaId,
        )

@dataclass
class MeetingContext:
    topic: str
    agendas: dict[str, AgendaItemModel]  # agenda_id -> AgendaItemModel
    host: str
    participants: list[UserInfo]
    chats: dict[str, list[ChatLog]]  # agenda_id -> 안건별 채팅 내역
