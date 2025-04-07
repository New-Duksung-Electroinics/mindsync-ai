# 커스텀 예외 정의
from .base import BaseCustomError

class GeminiCallError(BaseCustomError):
    status_code = 502
    message = "Gemini API 호출 중 오류가 발생했습니다."

class GeminiParseError(BaseCustomError):
    message = "Gemini 응답을 처리하는 중 오류가 발생했습니다."

class MongoAccessError(BaseCustomError):
    message = "MongoDB 접근 중 오류가 발생했습니다."

class PromptBuildError(BaseCustomError):
    message = "프롬프트 빌드 중 서버 내부 오류가 발생했습니다."
