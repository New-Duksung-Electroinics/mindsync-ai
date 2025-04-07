import traceback
import inspect
from functools import wraps
from fastapi.exceptions import RequestValidationError
from .base import BaseCustomError


def catch_and_raise(label: str, error_class: type, skip_types: tuple[type] = ()):
    """
    주어진 함수 실행 중 발생한 예외를 감싸서 지정된 커스텀 에러로 변환하는 데코레이터

    - 에러 메시지 앞에 설명 문자열(label)을 추가하여 traceback과 함께 상세 에러 로그를 출력
    - 기본적으로 프로젝트의 주요 커스텀 에러는 다시 감싸지 않고 그대로 전달 (skip)
    - 예상하지 못한 일반 Exception만 지정한 error_class로 감싸서 전달
    - 동기/비동기 함수 모두 처리 가능

    Args:
        label: 주어진 함수 작업에 대한 설명 문자열
        error_class: 함수 실행 중 감싸서 던질 커스텀 예외 클래스
        skip_types: 감싸지 않고 그대로 raise할 예외 클래스들. 기본값으로 주요 커스텀 예외가 포함됨

    Returns:
        Callable: 예외 감싸기를 적용한 함수
    """
    skip = (BaseCustomError, RequestValidationError, ) + skip_types

    def decorator(func):
        if inspect.iscoroutinefunction(func):
            # 비동기 함수 처리 wrapper
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except skip:
                    print(f"[{label} 에러]", traceback.format_exc())
                    raise  # skip에 포함된 예외는 그대로 전파
                except Exception as e:
                    print(f"[{label} 에러]", traceback.format_exc())
                    raise error_class()  # str(e)
            return async_wrapper
        else:
            # 동기 함수 처리 wrapper
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except skip:
                    print(f"[{label} 에러]", traceback.format_exc())
                    raise  # skip에 포함된 예외는 그대로 전파
                except Exception as e:
                    print(f"[{label} 에러]", traceback.format_exc())
                    raise error_class()  # str(e)
            return sync_wrapper
    return decorator
