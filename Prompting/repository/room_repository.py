from .mongo_client import db, ROOM_COLLECTION
from Prompting.exceptions.errors import MongoAccessError
from Prompting.exceptions.decorators import catch_and_raise

class RoomRepository:
    def __init__(self):
        self.collection = db[ROOM_COLLECTION]

    @catch_and_raise("MongoDB 채팅방 정보 조회", MongoAccessError)
    async def get_room_info(self, room_id: str) -> dict:
        """채팅방 ID로 해당 방의 정보를 조회"""
        doc = await self.collection.find_one({"roomId": room_id})
        return doc

    @catch_and_raise("MongoDB 회의 요약 저장", MongoAccessError)
    async def save_summary(self, room_id: str, summary: list[dict]):
        """
        room_id를 가진 채팅방 문서에 'summary' 필드 추가 또는 갱신

        Args:
            room_id: 채팅방 ObjectId
            summary: 저장할 요약 데이터
        """
        result = await self.collection.update_one(
            {"roomId": room_id},
            {"$set": {"summary": summary}}
        )
        if result.modified_count == 0:
            if result.upserted_id is not None:
                print(f"새로 insert된 문서 ID: {result.upserted_id}")
            else:
                raise MongoAccessError("회의 요약 저장 실패")
