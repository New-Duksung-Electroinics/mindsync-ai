# 🧑‍💻 Development Guide

> MindSync AI 백엔드 모듈(Prompting)의 구조, 스타일, 예외 처리 및 모듈화 전략 가이드

---

## ✍️ 코드 작성 스타일

### ✅ 네이밍 규칙

| 항목           | 예시                  | 설명 |
|--------------|---------------------|------|
| 클래스          | `AgendaGenerator`   | `UpperCamelCase` 사용 |
| 함수           | `generate_summary`  | `snake_case` 사용 |
| 파일    | `agenda_generator.py` | `snake_case` 사용 |
| 디렉터리    | `services/`         | `snake_case` 사용 |
| 상수           | `DEFAULT_MODEL_NAME` | `UPPER_SNAKE_CASE` 사용 |
- 서비스 객체, 리포지트리 등 **단일 클래스 정의 파일**은 클래스명과 동일하게 사용

### ✅ 타입 힌트 & 주석

- 모든 함수에 **타입 힌트 필수**
- 클래스/함수 상단에 Google 스타일 주석 사용

```python
def generate_agenda(self, topic_request: str) -> list[dict]:
    """
    회의 주제에 대한 설명을 바탕으로 추천 안건 목록을 생성

    Args:
        topic_request: 회의 주제에 대한 설명이 포함된 텍스트

    Returns:
        안건 데이터 리스트
    """
```

---

## 🧹 예외 처리 전략

### ✅ 예외 계층

| Exception Class | 설명 |
|-----------------|------|
| `GeminiCallError` | Gemini API 요청 실패 시 |
| `GeminiParseError` | Gemini 응답 파싱 실패 시 |
| `PromptBuildError` | 프롬프트 구성 로직 실패 시 |
| `MongoAccessError` | DB 접근 실패 시 |

- 모든 커스텀 예외는 `custom_exception_handler`에서 공통 처리

### ✅ 데코레이터 기반 예외 래핑

```python
@catch_and_raise("회의 요약 저장", MongoAccessError)
async def save_summary(...):
    ...
```

> 자세한 예외 처리는 `Prompting/exceptions/` 참조

---

## 📁 모듈 구조 전략

```bash
Prompting/
├── main.py            # FastAPI 진입점
├── di.py              # 의존성 주입
│
├── repository/        # MongoDB 접근
├── services/          # Gemini 기반 서비스
│   ├── context_builders/  # 프롬프트 context 빌더
│   └── templates/         # 프롬프트 템플릿
├── usecases/          # 데이터 흐름 및 도메인 처리
├── schemas/           # pydantic 기반 요청/응답 목록
├── exceptions/        # 커스텀 에러 및 핸들러
```

- **Repository**: DB와 통신 (Mongo → dict)
- **Usecase**: dict → 도메인 객체 변환 및 기능 흐름 관리
- **Service**: Gemini API 호출 및 응답 처리
- **context_builders**: 프롬프트용 context 빌더
- **templates**: 프롬프트 템플릿 관리

---
## 🤝 Contribution

현재는 Organization 내부 테스트용으로 사용되며, 외부 기여는 받지 않습니다.
다만 코드 스타일/구조 관련 피드백은 언제든지 환영합니다.