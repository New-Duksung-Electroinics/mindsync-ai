from pydantic import BaseModel

class SummaryRequest(BaseModel):
    roomId: str
    is_last_agenda_skipped: bool = False