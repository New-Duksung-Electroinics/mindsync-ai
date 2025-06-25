from pydantic import BaseModel
from Prompting.common import AgendaStatus

class AgendaItemModel(BaseModel):
    title: str
    status: AgendaStatus

