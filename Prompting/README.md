# 🧠 Prompting Module

> 회의 지원 AI 기능을 Google Gemini API와 함께 구성한 핵심 모듈

---

## 📌 모듈 개요

이 모듈은 FastAPI 기반의 AI 백엔드 서버로, Gemini API를 통해 다음과 같은 기능을 제공하며,
이 과정에서 회의 주제·채팅·AI 봇의 MBTI 성향 정보를 활용합니다.

- **회의 안건 생성** (`AgendaGenerator`)
- **회의 요약 생성** (`MeetingSummarizer`)
- **MBTI 기반 챗봇 채팅 생성** (`MbtiChatGenerator`)

---

## 📂 디렉토리 구조

```bash
Prompting/
├── main.py               # FastAPI 진입점
├── di.py                 # DI (의존성 주입) 설정
│
├── repository/           # MongoDB 연동 (motor)
│   ├── chat_repository.py
│   ├── agenda_repository.py
│   ├── room_repository.py
│   ├── user_repository.py
│   └── mongo_client.py
│
├── services/             # 핵심 서비스 로직 (Gemini 호출)
│   ├── agenda_generator.py
│   ├── meeting_summarizer.py
│   ├── mbti_chat_generator.py
│   ├── gemini_client.py
│   ├── context_builders/   # 프롬프트 context 생성기
│   └── templates/          # 프롬프트 템플릿
│
├── usecases/            # 도메인 객체 구성 및 기능별/공통 흐름 처리
│   ├── meeting_context.py
│   └── ...
│
├── schemas/             # 요청/응답 데이터 구조
├── exceptions/          # 공통 에러 및 핸들러
├── common/              # 편의를 위한 공통 모듈
└── README.md            # (현재 문서)
```

---

## ⚙️ 주요 클래스

| 분류                  | 클래스                      | 설명                     |
|---------------------|-----------------------------|------------------------|
| `services/`         | `AgendaGenerator`           | 주제 기반 회의 안건 생성         |
|                     | `MeetingSummarizer`         | 채팅 로그 기반 회의 요약 생성      |
|                     | `MbtiChatGenerator`         | MBTI 성격 특징 기반 챗봇 발화 생성 |
| `context_builders/` | `MeetingHistoryBuilder`     | 채팅 기록 → 프롬프트용 문자열 가공   |
|                     | `MbtiTraitBuilder`          | MBTI 성향 요약 텍스트 구성      |
| `repository/`       | `ChatRepository`, ...       | MongoDB 데이터 접근 객체      |
| `usecases/`         | `load_summary_context`, ... | 데이터 흐름과 도메인 객체 조합 로직   |

---

## 🔑 환경 변수 설정 (.env)

```bash
GEMINI_API_KEY=your-google-api-key
MONGO_URI=mongodb://...
```

---
## 🚀 실행 예시
```bash
uvicorn Prompting.main:app --host 0.0.0.0 --port 8000
```
---
## 📚 문서 모음

| 문서                                                      | 설명                        |
|---------------------------------------------------------|---------------------------|
| [`architecture.md`](./docs/architecture.md)             | 전체 시스템 구성과 모듈 관계 설명       |
| [`dataflow.md`](./docs/dataflow.md)                     | 사용자의 요청 → 응답까지의 흐름 정리     |
| [`prompting_strategy.md`](./docs/prompting_strategy.md) | Gemini 프롬프팅 전략 가이드        |
| [`api_spec.md`](./docs/api_spec.md)                     | FastAPI 기반 API 명세서        |
| [`GIT_GUIDE.md`](./docs/GIT_GUIDE.md)                   | 브랜치 전략, 커밋 컨벤션, PR 작성 가이드 |
| [`DEVELOPMENT_GUIDE.md`](./docs/DEVELOPMENT_GUIDE.md)   | 코드 스타일, 예외 처리, 구조 설계 가이드  |




