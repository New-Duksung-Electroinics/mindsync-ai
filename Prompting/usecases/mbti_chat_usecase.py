# MBTI 참여자 챗 생성 하위 use case 모음
from Prompting.schemas import ChatRequest
from Prompting.repository import ChatRepository, RoomRepository, UserRepository, AgendaRepository
from Prompting.usecases.usecase_utils import load_meeting_room_info, load_participants_info
from Prompting.usecases.meeting_context import MeetingContext, ChatLog
from Prompting.exceptions import catch_and_raise, MongoAccessError
from fastapi.exceptions import RequestValidationError
from Prompting.common import AgendaStatus


@catch_and_raise("MongoDB 데이터 로딩", MongoAccessError)
async def load_chat_context_and_update_agenda_status(
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

    chats = []
    if request.agendaId != '1':  # 첫 번째 안건이 아닌 경우에만
        # 직전 안건의 상태 업데이트
        prev_agenda_id = str(int(request.agendaId) - 1)
        agendas = await agenda_repo.update_status(request.roomId, prev_agenda_id, request.is_previous_skipped)

        # 직전 안건이 생략되지 않고 논의 완료로 처리되었으면, 직전 채팅 내역을 맥락으로 참조.
        if not request.is_previous_skipped:
            chat_data = await chat_repo.get_chat_logs_by_agenda_id(request.roomId, prev_agenda_id)
            chats = [ChatLog.from_model(c) for c in chat_data]

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

