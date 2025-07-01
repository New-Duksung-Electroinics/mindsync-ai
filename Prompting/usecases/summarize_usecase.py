# 요약 생성 요청 시 활용되는 하위 Use Case 모음
from Prompting.repository import ChatRepository, RoomRepository, UserRepository, AgendaRepository
from Prompting.usecases.usecase_utils import load_participants_info
from Prompting.usecases.meeting_context import MeetingContext, ChatLog
from Prompting.exceptions import catch_and_raise, MongoAccessError
from Prompting.schemas import SummaryRequest


@catch_and_raise("MongoDB 데이터 로딩", MongoAccessError)
async def load_summary_context_and_update_agenda_status(
        request: SummaryRequest,
        chat_repo: ChatRepository,
        agenda_repo: AgendaRepository,
        room_repo: RoomRepository,
        user_repo: UserRepository
) -> MeetingContext:
    """
    회의 요약 생성 요청에 필요한 데이터를 MongoDB에서 읽어와 MeetingContext로 재구성

    Args:
        room_id: 회의를 진행한 채팅방 ID
        chat_repo: 채팅 데이터 관리 객체
        agenda_repo: 안건 데이터 관리 객체
        room_repo: 채팅방 데이터 관리 객체
        user_repo: 사용자 데이터 관리 객체

    Returns:
        회의 맥락이 담긴 MeetingContext 데이터 (주제, 안건, 채팅 내역, 주최자와 참여자)
    """

    # 해당 회의의 안건 데이터와 전체 채팅 내역 읽어오기
    agendas = await agenda_repo.get_agenda_by_room(request.roomId)
    chat_data = await chat_repo.get_chat_logs_by_room(request.roomId)
    chats = [ChatLog.from_model(c) for c in chat_data]

    # 마지막 안건의 상태 업데이트
    last_agenda_id = str(len(agendas))
    await agenda_repo.update_status(request.roomId, last_agenda_id, request.is_last_agenda_skipped)

    # 회의 참여자 정보(이메일, 이름, mbti) 불러오기
    room_model = await room_repo.get_room_info(request.roomId)
    participants = await load_participants_info(room_model.participants, user_repo)

    return MeetingContext(
        topic=room_model.content,
        agendas=agendas,
        host=room_model.host,
        participants=participants,
        chats=chats
    )

