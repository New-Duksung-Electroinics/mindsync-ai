from pydantic import BaseModel
from typing import Any, Optional

class Response(BaseModel):
    status: str
    message: str
    data: Optional[Any] = None