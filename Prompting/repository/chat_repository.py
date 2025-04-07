from .mongo_client import db, CHAT_COLLECTION
from bson import ObjectId
from Prompting.exceptions.errors import MongoAccessError
from Prompting.exceptions.decorators import catch_and_raise

class ChatRepository:
    def __init__(self):
        self.collection = db[CHAT_COLLECTION]

    @catch_and_raise("MongoDB 전체 채팅 조회", MongoAccessError)
    async def get_chat_logs_by_room(self, room_id: str) -> list[dict]:
        """채팅방 ID 기준으로 해당 방의 채팅 기록을 시간 순서대로 조회 (최대 1000개까지)"""
        cursor = self.collection.find({"roomId": ObjectId(room_id)}).sort("timestamp", 1)
        return await cursor.to_list(length=1000)

    @catch_and_raise("MongoDB 직전 안건 채팅 조회", MongoAccessError)
    async def get_chat_logs_of_previous_agenda(self, room_id: str, current_agenda_id: str) -> list[dict]:
        """
        현재 안건 ID 기준, 직전 안건의 채팅 기록을 시간 순으로 조회

        Args:
            room_id: 채팅방 ID
            current_agenda_id: 현재 안건 ID

        Returns:
            직전 안건에 해당하는 채팅 기록 리스트
        """

        try:  # 현재 agenda_id를 int로 변환 (str로 들어와도 대비)
            current_agenda_num = int(current_agenda_id)
        except ValueError:
            raise ValueError("agenda_id는 숫자 형태의 문자열 또는 정수여야 합니다.")

        # 해당 채팅방에서 current_agenda_id의 직전 안건에 대한 모든 chat을 시간 순으로 정렬해 불러오기
        cursor = self.collection.find({
            "roomId": ObjectId(room_id),
            "agenda_id": str(current_agenda_num - 1)  # MongoDB 저장이 str이라면
        }).sort("timestamp", 1)

        return await cursor.to_list(length=1000)
