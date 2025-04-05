from .mongo import db
from Prompting.exceptions.errors import MongoAccessError
from Prompting.exceptions.decorators import catch_and_raise

class UserRepository:
    def __init__(self):
        self.collection = db["user"]

    @catch_and_raise("MongoDB 참여자 정보 목록 조회", MongoAccessError)
    async def get_user_list_by_emails(self, emails: list[str]) -> list[dict]:
        cursor = self.collection.find({"email": {"$in": emails}})
        users = await cursor.to_list(length=len(emails))

        return [
            {
                "email": user.get("email", ""),
                "name": user.get("username", "")
            }
            for user in users
        ]