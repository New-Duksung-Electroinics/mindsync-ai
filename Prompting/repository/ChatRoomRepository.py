from typing import List
from .mongo import db
from bson import ObjectId
from Prompting.exceptions.errors import MongoAccessError
from Prompting.exceptions.decorators import catch_and_raise

class ChatRoomRepository:
    def __init__(self):
        self.collection = db["chatroom"]

    @catch_and_raise("MongoDB 채팅방 조회", MongoAccessError)
    async def get_room_info(self, room_id: str) -> dict:
        doc = await self.collection.find_one({"_id": ObjectId(room_id)})
        return doc

    @catch_and_raise("MongoDB 채팅방에 요약 저장", MongoAccessError)
    async def save_summary_by_room_id(self, room_id: str, summary: List[dict]) -> bool:
        """
        해당 roomId의 chatroom 문서에 'summary' 필드 추가 또는 갱신
        :param room_id: 채팅방 ObjectId (str)
        :param summary: 저장할 요약 데이터 (dict 리스트)
        :return: 성공 여부 (bool)
        """
        result = await self.collection.update_one(
            {"_id": ObjectId(room_id)},
            {"$set": {"summary": summary}}
        )
        return result.modified_count > 0