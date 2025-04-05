from .mongo import db
from typing import List
from bson import ObjectId
from Prompting.exceptions.errors import MongoAccessError
from Prompting.exceptions.decorators import catch_and_raise

class ChatRepository:
    def __init__(self):
        self.collection = db["chat"]

    @catch_and_raise("MongoDB 전체 채팅 조회", MongoAccessError)
    async def get_chat_logs_by_room(self, room_id: str) -> List[dict]:
        cursor = self.collection.find({"roomId": ObjectId(room_id)})
        return await cursor.to_list(length=1000)

    @catch_and_raise("MongoDB 직전 안건 채팅 조회", MongoAccessError)
    async def get_chat_logs_of_previous_agenda(self, room_id: str, current_agenda_id: str) -> list:

        try:  # 현재 agenda_id를 int로 변환 (str로 들어와도 대비)
            current_agenda_num = int(current_agenda_id)
        except ValueError:
            raise ValueError("agenda_id는 숫자 형태의 문자열 또는 정수여야 합니다.")

        # 해당 채팅방의 모든 chat을 시간 순으로 정렬해 불러오기
        cursor = self.collection.find({"roomId": ObjectId(room_id)}).sort("timestamp", 1)
        chats = await cursor.to_list(length=1000)  # 비동기로 리스트 변환(1000개 제한 주의)

        # Python 쪽에서 agenda_id를 숫자로 바꿔서 비교
        filtered_chats = []
        for chat in chats:
            try:
                agenda_num = int(chat.get("agenda_id", -1))  # 없을 경우 -1로 처리
                if agenda_num == current_agenda_num - 1:  # 바로 직전 번호만
                    filtered_chats.append(chat)
            except (ValueError, TypeError):
                continue  # agenda_id가 변환 불가능하면 무시

        return filtered_chats
