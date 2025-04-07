from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .base import BaseCustomError
import traceback


async def custom_exception_handler(_request: Request, exc: BaseCustomError):
    """커스텀 에러 발생 시 에러 응답을 만드는 예외 핸들러"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "ERROR",
            "message": exc.message,
            "data": None
        }
    )


async def request_validation_exception_handler(_request: Request, exc: RequestValidationError):
    """API Request 처리 중 예외 발생 시 에러 응답을 만드는 예외 핸들러 """
    def get_field_name(loc):
        return ".".join(loc[1:]) if loc and loc[0] == "body" else ".".join(loc)

    errors = exc.errors()
    message_parts = [
        f"{get_field_name(err['loc'])}: {err['msg']}" for err in errors  # 에러가 발생한 입력 필드에 대한 메세지 생성
    ]
    full_message = " / ".join(message_parts)

    return JSONResponse(
        status_code=422,
        content={
            "status": "ERROR",
            "message": full_message or "입력 값이 올바르지 않습니다.",
            "data": None
        }
    )


async def general_exception_handler(_request: Request, _exc: Exception):
    """예기치 못한 예외 발생 시 에러 응답을 만드는 예외 핸들러"""
    print("[Unhandled Exception]", traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "status": "ERROR",
            "message": "알 수 없는 서버 오류가 발생했습니다.",
            "data": None
        }
    )

