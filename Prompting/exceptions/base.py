# 커스텀 에러 공통 클래스

class BaseCustomError(Exception):
    status_code = 500
    message = "서버 내부 오류가 발생했습니다."

    def __init__(self, message: str = None):
        self.message = message or self.message
        super().__init__(self.message)