from pydantic import BaseModel

class ChatGenRequest(BaseModel):
    roomId: str
    agendaId: str