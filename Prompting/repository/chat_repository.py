from .mongo_client import db, CHAT_COLLECTION
from Prompting.exceptions.errors import MongoAccessError
from Prompting.exceptions.decorators import catch_and_raise
from Prompting.models import ChatMessage, RoomMessages
from collections import OrderedDict


class ChatRepository:
    def __init__(self):
        self.collection = db[CHAT_COLLECTION]

    @catch_and_raise("MongoDB 전체 채팅 조회", MongoAccessError)
    async def get_chat_logs_by_room(self, room_id: str) -> OrderedDict[str, list[ChatMessage]]:
        """채팅방 ID 기준으로 해당 방의 전체 채팅 기록을 시간 순서대로 조회. 안건 ID-채팅내역 맵을 반환."""

        doc = await self.collection.find_one({"_id": room_id})
        if doc is None:
            raise MongoAccessError(f"roomId '{room_id}'에 해당하는 채팅 데이터 없음")

        room_msgs = RoomMessages(**doc)
        agenda_chat_map = room_msgs.messages

        # 각 agenda의 채팅 리스트를 timestamp 기준 정렬
        for aid in agenda_chat_map:
            agenda_chat_map[aid].sort(key=lambda chat: chat.timestamp)

        sorted_agenda_chat_map = sorted(agenda_chat_map.items(), key=lambda item: int(item[0]))  # agenda_id 정렬
        return OrderedDict(sorted_agenda_chat_map)


    @catch_and_raise("MongoDB 지정 안건 채팅 조회", MongoAccessError)
    async def get_chat_logs_by_agenda_id(self, room_id: str, agenda_id: str) -> dict[str, list[ChatMessage]]:
        """특정 안건에 대한 채팅 기록을 시간 순으로 조회"""

        doc = await self.collection.find_one({"_id": room_id})
        if doc is None:
            raise MongoAccessError(f"roomId '{room_id}'에 해당하는 채팅 데이터 없음")

        room_msgs = RoomMessages(**doc)
        return {agenda_id: sorted(room_msgs.messages[agenda_id], key=lambda chat: chat.timestamp)}

