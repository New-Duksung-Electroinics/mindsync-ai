from pydantic import BaseModel

class ChatRequest(BaseModel):
    roomId: str
    agendaId: str
    is_previous_skipped: bool = False