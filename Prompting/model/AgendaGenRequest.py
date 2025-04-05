from pydantic import BaseModel

class AgendaGenRequest(BaseModel):
    roomId: str
    description: str