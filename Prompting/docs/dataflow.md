# 🔄 데이터 흐름 개요

> 이 문서는 사용자의 요청이 어떻게 FastAPI 서버를 통해 처리되어 응답으로 전달되는지를 단계적으로 설명합니다.

---

### 1. 사용자의 요청 발생

- 프론트엔드에서 특정 기능에 대한 요청 전송 (예: 회의 요약, MBTI 챗봇 채팅 등)
- HTTP POST 요청이 FastAPI 서버에 도달

---

### 2. 엔드포인트 진입 (FastAPI `main.py`)

- 요청 body가 `pydantic` 기반 `schemas/`로 검증됨
- DI 기반으로 서비스 객체 및 Repository 주입 (`di.py`)
- 적절한 서비스 객체를 통해 기능 처리 시작

---

### 3. Usecase 흐름

- `usecases/`에서 요청의 맥락을 구성 (`meeting_context` 등)
- Repository를 통해 DB에서 필요한 데이터 조회
- 맥락 데이터 조회가 필요없는 안건 생성 기능은 이 과정이 생략됨

---

### 4. Prompt 빌드 및 AI 호출

- `services/` 내부에서 프롬프트 템플릿 조립
- `context_builders/`를 통해 회의 맥락/참여자 정보 구조화
- `GeminiClient`를 통해 Gemini API 호출

---

### 5. 결과 처리 및 저장

- Gemini 응답을 내부 저장 형식에 맞게 파싱
- Repository를 통해 MongoDB에 저장 (`agenda`, `summary`)

---

### 6. 최종 응답 반환

- `success_response()` 포맷으로 JSON 반환
- 구조: `{"status": "SUCCESS", "message": "...", "data": ...}`
