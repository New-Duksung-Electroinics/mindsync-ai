# 🏗️ 시스템 아키텍처

> 이 문서는 MindSync AI 모듈(Prompting)의 전체 구성과 주요 컴포넌트 관계를 설명합니다.

---

## 1. 개요

- FastAPI 기반의 AI 백엔드
- Google Gemini API를 통한 프롬프트 기반 서비스
- MongoDB를 통한 데이터 저장

---

## 2. 시스템 구성도
주요 컴포넌트 간 관계를 나타낸 구조:
```bash
[Client (웹 프론트엔드)]
        │
        ▼
[FastAPI 서버: main.py]
        │
        ├── [API Endpoint: /agenda_generation, /summarize, /mbti_chat]
        │
        ├── di.py (의존성 주입)
        │
        ├── services/
        │     ├── agenda_generator.py
        │     ├── mbti_chat_generator.py
        │     ├── meeting_summarizer.py
        │     └── gemini_client.py
        │
        ├── services/context_builders/
        │     ├── meeting_history_builder.py
        │     └── mbti_trait_builder.py
        │
        ├── services/templates/
        │     └── (프롬프트 문자열 템플릿 관리)
        │
        ├── usecases/
        │     ├── summarize_usecase.py
        │     ├── mbti_chat_usecase.py
        │     └── meeting_context.py
        │
        ├── repository/
        │     ├── agenda_repository.py
        │     ├── chat_repository.py
        │     ├── room_repository.py
        │     └── user_repository.py
        │
        ├── schemas/
        │     └── 요청/응답 객체 모델 정의 (Pydantic)
        │
        └── exceptions/
              └── 에러 처리 및 공통 예외 정의


```



---

## 3. 주요 구성요소 설명

- **`main.py`**: 라우팅, 의존성 주입, 예외 처리 등록
- **`services/`**: 주요 AI 기능 구현
- **`usecases/`**: 도메인 흐름을 조립 (컨텍스트 준비 등)
- **`repository/`**: DB 접근 책임 담당
- **`context_builders/`**: 회의/참여자 정보 가공
- **`templates/`**: 프롬프트 다국어/기능별 템플릿

---

## 4. 주요 설계 원칙

- **의존성 분리**: `di.py`를 통해 서비스 및 레포지토리 객체 관리
- **역할 기반 구조화**: `services`, `repository`, `usecases`, `schemas`, `exceptions` 분리
- **프롬프트 중심 설계**: Gemini API 연동을 위한 `context_builders`, `templates` 모듈 도입
- **낮은 결합도 & 높은 응집도**: 모듈 간 직접 의존 최소화

---


## 5. 확장 고려

- 서비스 단위 분리로 기능별 테스트 용이
- Prompting 이외에도 sLLM, 챗봇 기능 확장 가능


