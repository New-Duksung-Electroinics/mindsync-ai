from pydantic import BaseModel

class RoomIdRequest(BaseModel):
    roomId: str