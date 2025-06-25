from .mongo_client import db, AGENDA_COLLECTION
from Prompting.exceptions import MongoAccessError, catch_and_raise
from Prompting.common import AgendaStatus
from pymongo import ReturnDocument
from Prompting.models import AgendaItemModel


class AgendaRepository:
    def __init__(self):
        self.collection = db[AGENDA_COLLECTION]

    @catch_and_raise("MongoDB 안건 저장", MongoAccessError)
    async def save_agenda(self, room_id: str, agenda_dict: dict[str, str]) -> dict[str, str]:
        """
        안건 데이터를 MongoDB agenda 콜렉션에 저장

        Args:
            room_id: 해당 안건과 연관된 회의 채팅방 ID
            agenda_dict: [안건 ID]-[안건명]이 매핑된 dict

        Returns:
            [안건 ID]-[안건명]이 매핑된 dict (예비 안건을 포함해 실제 저장된 안건 데이터)
        """
        # 마지막 요소로 추가 논의를 위한 예비 안건 추가
        last_agenda_id = str(len(agenda_dict) + 1)
        agenda_dict[last_agenda_id] = "예비 안건 (회의 중 추가 논의 시)"

        agenda_data = {}  # DB 저장용 (안건명과 논의 상태를 함께 저장)
        for aid in agenda_dict:
            title = agenda_dict[aid]
            agenda_data[aid] = {
                "title": title,
                "status": AgendaStatus.PENDING.value
            }

        result = await self.collection.update_one(
            {"_id": room_id},  # 검색 기준
            {"$set": {"roomId": room_id, "agendas": agenda_data}},  # 갱신 필드
            upsert=True  # 없으면 새로 insert
        )

        if result.modified_count == 0 and result.upserted_id is None:
            raise MongoAccessError("회의 안건 저장 실패")

        return agenda_dict  # 반환은 [안건 ID]-[안건명]이 매핑된 dict만


    @catch_and_raise("MongoDB 안건 조회", MongoAccessError)
    async def get_agenda_by_room(self, room_id: str) -> dict[str, AgendaItemModel]:
        """채팅방 ID를 기반으로 해당 방의 안건 데이터를 검색"""
        doc = await self.collection.find_one({"roomId": room_id})
        if doc is None:
            raise MongoAccessError(f"roomId '{room_id}'에 해당하는 안건 데이터 없음")
        return {
            aid: AgendaItemModel(**item)
            for aid, item in doc.get("agendas", {}).items()
        }


    @catch_and_raise("MongoDB 안건 상태 업데이트", MongoAccessError)
    async def update_status(self, room_id: str, agenda_id: str, is_skipped: bool):
        """
        안건 데이터에서 특정 안건의 논의 상태를 완료 또는 생략 상태로 업데이트

        Args:
            room_id: 채팅방 ObjectId
            agenda_id: 상태를 수정할 안건 ID
            is_skipped: 안건의 생략 여부. 생략이 아니면 완료로 처리
        """
        status = AgendaStatus.SKIPPED if is_skipped else AgendaStatus.COMPLETE
        updated_agendas = await self.collection.find_one_and_update(
            {"_id": room_id},
            {"$set": {f"agendas.{agenda_id}.status": status.value}},
            projection={"agendas": 1, "_id": 0},
            return_document=ReturnDocument.AFTER  # 업데이트 후의 값을 반환
        )
        if updated_agendas is None:
            raise MongoAccessError("안건 상태 업데이트 실패")

