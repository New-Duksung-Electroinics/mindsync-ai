# 요약 생성 요청 시 활용되는 하위 Use Case 모음
from Prompting.repository import ChatRepository, RoomRepository, UserRepository, AgendaRepository
from Prompting.usecases.usecase_utils import load_meeting_room_info, load_participants_info
from Prompting.usecases.meeting_context import MeetingContext, ChatLog
from Prompting.exceptions import catch_and_raise, MongoAccessError


@catch_and_raise("MongoDB 데이터 로딩", MongoAccessError)
async def load_summary_context(
        room_id: str,
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
    agenda_data = await agenda_repo.get_agenda_by_room(room_id)
    chat_data = await chat_repo.get_chat_logs_by_room(room_id)
    chats = [ChatLog.from_dict(c) for c in chat_data]

    # 회의 참여자 정보(이메일, 이름, mbti) 불러오기
    room = await load_meeting_room_info(room_id, room_repo)
    participants = await load_participants_info(room.participants, user_repo)

    return MeetingContext(
        topic=room.content,
        agendas=agenda_data["agendas"],
        host=room.host,
        participants=participants,
        chats=chats
    )

