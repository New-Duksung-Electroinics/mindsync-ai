# use case에서 쓰이는 data class 정의 모음
from dataclasses import dataclass

@dataclass
class RoomInfo:
    content: str
    host: str
    participants: list[str]  # host 포함

    @classmethod
    def from_dict(cls, data: dict) -> "RoomInfo":
        return cls(
            content=data.get("content", ""),
            host=data.get("host", ""),
            participants=data.get("participants", []) + [data.get("host", "")]
        )

@dataclass
class UserInfo:
    email: str
    name: str
    mbti: str

    @classmethod
    def from_dict(cls, data: dict) -> "UserInfo":
        return cls(
            email=data.get("email", ""),
            name=data.get("username", ""),
            mbti=data.get("usermbti", "")
        )

@dataclass
class ChatLog:
    sender: str
    message: str
    agenda_id: str

    @classmethod
    def from_dict(cls, data: dict) -> "ChatLog":
        return cls(
            sender=data.get("email", ""),
            message=data.get("message", ""),
            agenda_id=data.get("agenda_id", "")
        )

@dataclass
class MeetingContext:
    topic: str
    agendas: dict
    host: str
    participants: list[UserInfo]
    chats: list[ChatLog]
