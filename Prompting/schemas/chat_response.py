from pydantic import BaseModel

class ChatResponse(BaseModel):
    roomId: str
    name: str
    email: str
    message: str
    agenda_id: str