from fastapi.responses import JSONResponse
from typing import Optional, Any


def success_response(data: Optional[Any] = None, message: str = "요청이 성공했습니다."):
    return JSONResponse(
        status_code=200,
        content={
            "status": "SUCCESS",
            "message": message,
            "data": data
        }
    )
