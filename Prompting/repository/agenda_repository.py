from .mongo_client import db, AGENDA_COLLECTION
from Prompting.exceptions import MongoAccessError, catch_and_raise

class AgendaRepository:
    def __init__(self):
        self.collection = db[AGENDA_COLLECTION]

    @catch_and_raise("MongoDB 안건 저장", MongoAccessError)
    async def save_agenda(self, room_id: str, agenda_dict: dict) -> str:
        """
        안건 데이터를 MongoDB agenda 콜렉션에 저장

        Args:
            room_id: 해당 안건과 연관된 회의 채팅방 ID
            agenda_dict: [안건 ID]-[안건명]이 매핑된 dict

        Returns:
            MongoDB에 저장된 안건 문서의 `_id` 필드 (문자열 형태)
        """
        # 마지막 요소로 추가 논의를 위한 예비 안건 추가
        last_agenda_id = str(len(agenda_dict) + 1)
        agenda_dict[last_agenda_id] = "예비 안건 (회의 중 추가 논의 시)"

        result = await self.collection.update_one(
            {"_id": room_id},  # 검색 기준
            {"$set": {"roomId": room_id, "agendas": agenda_dict}},  # 갱신 필드
            upsert=True  # 없으면 새로 insert
        )

        if result.modified_count == 0:
            if result.upserted_id is not None:
                print(f"새로 insert된 문서 ID: {result.upserted_id}")
            else:
                raise MongoAccessError("회의 안건 저장 실패")


    @catch_and_raise("MongoDB 안건 조회", MongoAccessError)
    async def get_agenda_by_room(self, room_id: str) -> dict:
        """채팅방 ID를 기반으로 해당 방의 안건 데이터를 검색"""
        return await self.collection.find_one({"roomId": room_id})