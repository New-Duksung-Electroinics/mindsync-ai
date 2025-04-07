from pydantic import BaseModel

class AgendaRequest(BaseModel):
    roomId: str
    description: str