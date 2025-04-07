# MBTI 참여자 챗 생성 하위 use case 모음
from Prompting.schemas import ChatRequest
from Prompting.repository import ChatRepository, RoomRepository, UserRepository, AgendaRepository
from Prompting.usecases.usecase_utils import load_meeting_room_info, load_participants_info
from Prompting.usecases.meeting_context import MeetingContext, ChatLog
from Prompting.exceptions import catch_and_raise, MongoAccessError, GeminiCallError
from fastapi.exceptions import RequestValidationError


@catch_and_raise("MongoDB 데이터 로딩", MongoAccessError)
async def load_chat_context(
        request: ChatRequest,
        chat_repo: ChatRepository,
        agenda_repo: AgendaRepository,
        room_repo: RoomRepository,
        user_repo: UserRepository
) -> MeetingContext:
    """
    MBTI 봇 채팅 생성 요청에 필요한 데이터를 MongoDB에서 읽어와 MeetingContext로 재구성

    Args:
        request: MBTI 봇 채팅 생성 요청
        chat_repo: 채팅 데이터 관리 객체
        agenda_repo: 안건 데이터 관리 객체
        room_repo: 채팅방 데이터 관리 객체
        user_repo: 사용자 데이터 관리 객체

    Returns:
        회의 맥락이 담긴 MeetingContext 데이터 (주제, 안건, 채팅 내역, 주최자와 참여자)
    """

    # 해당 회의의 안건 데이터 읽어와 요청에 포함된 안건 ID가 유효한지 검사
    agenda_data = await agenda_repo.get_agenda_by_room(request.roomId)
    if request.agendaId not in agenda_data.get('agendas').keys():
        raise RequestValidationError([{"loc": ["agendaId"], "msg": "유효하지 않은 안건 번호", "type": "value_error"}])

    # 이전에 논의한 안건이 있으면 직전 안건에 대한 채팅 내역을 불러오기
    chats = []
    if request.agendaId != '1':
        chat_data = await chat_repo.get_chat_logs_of_previous_agenda(request.roomId, request.agendaId)
        chats = [ChatLog.from_dict(c) for c in chat_data]

    # 회의 참여자 정보(이메일, 이름, mbti) 불러오기
    room = await load_meeting_room_info(request.roomId, room_repo)
    participants = await load_participants_info(room.participants, user_repo)

    return MeetingContext(
        topic=room.content,
        agendas=agenda_data["agendas"],
        host=room.host,
        participants=participants,
        chats=chats
    )


@catch_and_raise("Gemini 챗 생성", GeminiCallError)
async def generate_chat(request, dataloader, mbti, bot):
    return await bot.generate_chat(dataloader, mbti, request.agendaId)

