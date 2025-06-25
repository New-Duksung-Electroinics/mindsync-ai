from pydantic import BaseModel


class UserModel(BaseModel):
    email: str
    username: str
    usermbti: str

    class Config:
        extra = "ignore"