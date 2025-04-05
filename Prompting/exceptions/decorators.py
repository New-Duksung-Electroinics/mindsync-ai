"""
함수 예외 처리 데코레이터
"""

import traceback
from functools import wraps
from fastapi.exceptions import RequestValidationError

def catch_and_raise(label: str, error_class: Exception):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except RequestValidationError:
                raise
            except Exception as e:
                print(f"[{label} 에러]", traceback.format_exc())
                raise error_class()  # str(e)
        return wrapper
    return decorator
