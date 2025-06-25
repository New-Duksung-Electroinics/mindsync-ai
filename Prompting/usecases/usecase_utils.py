# 여러 use case에서 활용되는 공통 유틸 함수
from Prompting.repository import UserRepository
from Prompting.usecases.meeting_context import UserInfo


async def load_participants_info(email_list: list[str], user_repo: UserRepository) -> list[UserInfo]:
    """
    MongoDB에서 회의 참여자 정보 가져오기

    Args:
        email_list: 회의 참여자 이메일 목록
        user_repo: 사용자 데이터 관리 객체

    Returns:
        회의 참여자의 세부 정보 목록(이름, 이메일, mbti 포함)
    """
    user_data = await user_repo.get_user_list_by_emails(email_list)
    return [UserInfo.from_model(u) for u in user_data]
