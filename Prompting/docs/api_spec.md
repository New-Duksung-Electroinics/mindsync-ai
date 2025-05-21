# 📘 MindSync AI 백엔드 API 명세

> 본 문서는 FastAPI 기반 MindSync AI 서비스에서 제공하는 **3종 API**의 명세를 요약합니다.


## 📌 공통 응답 구조

```
{
  "status": "SUCCESS" | "ERROR",
  "message": "요청 결과 설명",
  "data": {...} | null
}
```

> Spring 백엔드 응답 구조와 동일한 형식

<br/>


## 📝 1. 회의 안건 생성
- **URL**: `POST /agenda_generation/`
- **설명**: 주제 설명 → 자동 안건 목록 생성

### ✅ 요청 Body
```
{
  "roomId": "xxxxxxxxxxxxxxxxxxx",
  "description": "AI 서비스 고도화를 위한 전략 회의를 할 예정입니다."
}
```

### 🔁 응답 예시
```
{
  "status": "SUCCESS",
  "message": "안건 생성을 완료했습니다.",
  "data": {
    "1": "AI 응용 영역 확장 전략",
    "2": "내부 서비스 자동화 방안",
    ...
  }
}
```

<br/>

## 📝 2. 회의 요약 생성
- **URL**: `POST /summarize/`
- **설명**: 채팅 로그 기반 전체 회의 요약 도출

### ✅ 요청 Body
```
{
  "roomId": "xxxxxxxxxxxxxxxxxxx",
  "is_last_agenda_skipped" : true   # 마지막 안건의 논의 생략 여부
}
```

### 🔁 응답 예시
```
{
  "status": "SUCCESS",
  "message": "요약 생성을 완료했습니다.",
  "data": [
    {
      "agendaId": "1",
      "topic": "AI 응용 영역 확장 전략",
      "content": "주요 발언: ...\n결론: ..."
    },
    ...
    {
      "agendaId": "5",
      "topic": "예비 안건 (회의 중 추가 논의 시)",
      "content": null    # 논의가 생략된 안건의 요약은 null 처리
    }
  ]
}
```

<br/>

## 📝 3. MBTI 봇 채팅 생성
- **URL**: `POST /mbti_chat/`
- **설명**: 참가자 MBTI 기반 챗봇 발언 생성

### ✅ 요청 Body
```
{
  "roomId": "string",
  "agendaId": "2",
  "is_previous_skipped" : false   # 직전 안건의 논의 생략 여부
}
```
### 🔁 응답 예시
```
{
  "status": "SUCCESS",
  "message": "MBTI 봇의 채팅 생성을 완료했습니다.",
  "data": {
    "roomId": "xxxxxxxxxxxxxxxxxxx",
    "name": "INFP",
    "email": "infp@ai.com",
    "message": "저는 이 부분이 정말 중요하다고 생각해요...",
    "agenda_id": "2"
  }
}
```

<br/>

## ❗ 에러 코드

| 코드  | 설명                  |
|-----|-----------------------|
| 422 | 요청 데이터 형식 오류     | 
| 500 | 서버 내부 처리 실패       | 
| 502 | Gemini API 호출 오류     | 

