from pydantic import BaseModel

class ChatRequest(BaseModel):
    roomId: str
    agendaId: str