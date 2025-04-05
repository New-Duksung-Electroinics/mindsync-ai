from typing import Optional
from .mongo import db
from bson import ObjectId
from Prompting.exceptions.errors import MongoAccessError
from Prompting.exceptions.decorators import catch_and_raise

class AgendaRepository:
    def __init__(self):
        self.collection = db["agenda"]

    @catch_and_raise("MongoDB 안건 저장", MongoAccessError)
    async def save_agenda(self, room_id: str, agenda_dict: dict) -> str:
        doc = {
            "roomId": room_id,
            "agendas": agenda_dict
        }
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)

    @catch_and_raise("MongoDB 안건 조회", MongoAccessError)
    async def get_agenda_by_id(self, room_id: str) -> Optional[dict]:
        try:
            object_id = ObjectId(room_id)
        except Exception:
            object_id = room_id  # fallback: 그냥 문자열로 시도

        return await self.collection.find_one({"roomId": object_id})