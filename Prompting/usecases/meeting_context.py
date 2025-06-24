# use case에서 쓰이는 data class 정의 모음
from dataclasses import dataclass
from Prompting.models import RoomModel, ChatModel, UserModel

@dataclass
class RoomInfo:
    content: str
    host: str
    participants: list[str]  # host 포함

    @classmethod
    def from_model(cls, model: RoomModel) -> "RoomInfo":
        return cls(
            content=model.content,
            host=model.host_email,
            participants=model.participants + [model.host_email]
        )

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
    def from_model(cls, model: ChatModel) -> "ChatLog":
        return cls(
            sender=model.email,
            message=model.message,
            agenda_id=model.agenda_id,
        )

@dataclass
class MeetingContext:
    topic: str
    agendas: dict
    host: str
    participants: list[UserInfo]
    chats: list[ChatLog]
