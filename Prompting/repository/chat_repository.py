from .mongo_client import db, CHAT_COLLECTION
from Prompting.exceptions.errors import MongoAccessError
from Prompting.exceptions.decorators import catch_and_raise

class ChatRepository:
    def __init__(self):
        self.collection = db[CHAT_COLLECTION]

    @catch_and_raise("MongoDB 전체 채팅 조회", MongoAccessError)
    async def get_chat_logs_by_room(self, room_id: str) -> list[dict]:
        """채팅방 ID 기준으로 해당 방의 채팅 기록을 시간 순서대로 조회 (최대 1000개까지)"""
        cursor = self.collection.find({"roomId": room_id}).sort("timestamp", 1)
        return await cursor.to_list(length=1000)

    @catch_and_raise("MongoDB 지정 안건 채팅 조회", MongoAccessError)
    async def get_chat_logs_by_agenda_id(self, room_id: str, agenda_id: str) -> list[dict]:
        """
        특정 안건에 대한 채팅 기록을 시간 순으로 조회

        Args:
            room_id: 채팅방 ID
            agenda_id: 채팅을 조회하려는 안건 ID

        Returns:
            특정 안건에 대한 채팅 기록 리스트
        """

        # 해당 채팅방에서 agenda_id 안건에 대한 모든 chat을 시간 순으로 정렬해 불러오기
        cursor = self.collection.find({
            "roomId": room_id,
            "agenda_id": agenda_id
        }).sort("timestamp", 1)

        return await cursor.to_list(length=1000)
