# DI 함수 정의
from Prompting.repository import AgendaRepository, ChatRepository, RoomRepository, UserRepository
from Prompting.services import AgendaGenerator, MeetingSummarizer, MbtiChatGenerator

def get_agenda_service():
    return AgendaGenerator()
def get_summarizer_service():
    return MeetingSummarizer()
def get_bot_service():
    return MbtiChatGenerator()
def get_agenda_repo():
    return AgendaRepository()
def get_chat_repo():
    return ChatRepository()
def get_room_repo():
    return RoomRepository()
def get_user_repo():
    return UserRepository()