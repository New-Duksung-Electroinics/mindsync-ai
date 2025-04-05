"""
커스텀 예외 정의
"""

class GeminiError(Exception):
    def __init__(self, message="Gemini 호출 또는 응답 파싱 중 오류가 발생했습니다."):
        self.message = message
        super().__init__(self.message)

class MongoAccessError(Exception):
    def __init__(self, message="MongoDB 접근 중 오류가 발생했습니다."):
        self.message = message
        super().__init__(self.message)

class DataLoaderError(Exception):
    def __init__(self, message="DataLoader 생성 중 오류가 발생했습니다."):
        self.message = message
        super().__init__(self.message)
