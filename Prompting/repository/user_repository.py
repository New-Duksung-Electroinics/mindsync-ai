from .mongo_client import db, USER_COLLECTION
from Prompting.exceptions.errors import MongoAccessError
from Prompting.exceptions.decorators import catch_and_raise
from Prompting.models import UserModel


class UserRepository:
    def __init__(self):
        self.collection = db[USER_COLLECTION]

    @catch_and_raise("MongoDB 참여자 정보 목록 조회", MongoAccessError)
    async def get_user_list_by_emails(self, emails: list[str]) -> list[UserModel]:
        """
        이메일 목록을 기준으로 사용자 정보를 조회

        Args:
            emails: 조회할 사용자 이메일 목록

        Returns:
            사용자 정보가 담긴 dict 객체 리스트
        """
        cursor = self.collection.find({"email": {"$in": emails}})
        docs = await cursor.to_list(length=None)
        return [UserModel.model_validate(doc) for doc in docs]