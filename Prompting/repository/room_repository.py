from .mongo_client import db, ROOM_COLLECTION
from Prompting.exceptions.errors import MongoAccessError
from Prompting.exceptions.decorators import catch_and_raise
from Prompting.models import RoomModel, AgendaSummaryModel


class RoomRepository:
    def __init__(self):
        self.collection = db[ROOM_COLLECTION]

    @catch_and_raise("MongoDB 채팅방 정보 조회", MongoAccessError)
    async def get_room_info(self, room_id: str) -> RoomModel:
        """채팅방 ID로 해당 방의 정보를 조회"""
        doc = await self.collection.find_one({"roomId": room_id})
        if doc is None:
            raise MongoAccessError(f"roomId '{room_id}'에 해당하는 채팅방 없음")
        return RoomModel(**doc)

    @catch_and_raise("MongoDB 회의 요약 저장", MongoAccessError)
    async def save_summary(self, room_id: str, summary: list[AgendaSummaryModel]):
        """
        room_id를 가진 채팅방 문서에 'summary' 필드 추가 또는 갱신

        Args:
            room_id: 채팅방 ObjectId
            summary: 저장할 요약 데이터
        """
        result = await self.collection.update_one(
            {"roomId": room_id},
            {"$set": {"summary": [item.dict() for item in summary]}}
        )
        if result.modified_count == 0 and result.upserted_id is None:
            raise MongoAccessError("회의 요약 저장 실패")
