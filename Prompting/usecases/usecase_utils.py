# 여러 use case에서 활용되는 공통 유틸 함수
from Prompting.repository import RoomRepository, UserRepository
from Prompting.usecases.meeting_context import RoomInfo, UserInfo


async def load_meeting_room_info(room_id: str, room_repo: RoomRepository) -> RoomInfo:
    """
    MongoDB에서 회의 채팅방 정보 가져오기

    Args:
        room_id: 채팅방 ID
        room_repo: 채팅방 데이터 관리 객체

    Returns:
        채팅방 정보(주최자, 참여자, 회의 주제 설명 포함)
    """
    room_data = await room_repo.get_room_info(room_id)
    return RoomInfo.from_dict(room_data)


async def load_participants_info(email_list: list[str], user_repo: UserRepository) -> list[UserInfo]:
    """
    MongoDB에서 회의 참여자 정보 가져오기

    Args:
        email_list: 회의 참여자 이메일 목록
        user_repo: 사용자 데이터 관리 객체

    Returns:
        회의 참여자의 세부 정보 목록(이름, 이메일, mbti 포함)
    """
    user_info_dicts = await user_repo.get_user_list_by_emails(email_list)
    return [UserInfo.from_dict(info) for info in user_info_dicts]
