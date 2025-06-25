from pydantic import BaseModel


class ChatModel(BaseModel):
    # _id: str
    # roomId: str
    # timestamp: str
    email: str
    # name: str
    message: str
    agenda_id: str

    class Config:
        extra = "ignore"

