# 🧠 MindSync AI Service

> **Prompting 기반 회의 지원 AI 백엔드 서비스**  
> Google Gemini API + FastAPI 기반으로, 자동화된 안건 및 회의 요약 생성, MBTI 성격 특징을 반영한 가상 참가자의 채팅 생성 기능을 제공합니다.



## 📌 프로젝트 소개

**MindSync**는 여러 AI 편의 기능을 지원하는 채팅 기반 회의 지원 플랫폼입니다.

Google Gemini API를 활용해 다음과 같은 편의 기능을 제공합니다:

- 주제 설명을 기반으로 한 **회의 안건 자동 생성**
- 채팅 로그 기반 **회의 요약 생성**
- MBTI 성격 유형 특징을 반영한 **AI 챗봇 발언 생성**

현재 이 레포는 **Prompting 기반 AI 처리 백엔드 모듈** 위주로 개발을 진행하고 있으며, 
추후 별도의 sLLM 모델 연구/개발로 확장될 여지가 있습니다.



## ⚙️ 기술 스택

| 구성 요소     | 기술                   |
|---------------|----------------------|
| Language      | Python 3.9+          |
| Web Framework | FastAPI              |
| LLM API       | Google Gemini API    |
| DB            | MongoDB (Motor)      |
| 패키지 관리    | pip + requirements.txt |
| 배포 환경     | Docker (개인 PC)       |

<br/>

## 🗂️ 디렉토리 구조

```bash
.
├── Dataset/            # (일시 중단) 전용 모델 학습을 위한 데이터셋 수집/전처리 폴더
├── Prompting/          # AI 기반 회의 지원 백엔드 모듈
│   ├── common/             # 공통 유틸 함수 및 enum 클래스 정의
│   ├── docs/               # Prompting 기반 백엔드 구조 설명, API 명세 등 문서
│   ├── exceptions/         # 공통 예외 클래스 및 핸들러 정의
│   ├── repository/         # MongoDB 연동
│   ├── schemas/            # 요청 및 응답 데이터 구조 정의
│   ├── scripts/            # 테스트 데이터 삽입 및 유틸리티 스크립트
│   ├── services/           # Gemini 기반 기능 서비스 (agenda, summary, mbti_chat)
│   ├── usecases/           # 도메인 중심 데이터 구성 및 흐름 처리
│   ├── di.py               # 의존성 주입 모듈
│   ├── main.py             # FastAPI 진입점
│   └── ...
├── requirements.txt
├── .env.template
├── dockerfile
└── README.md           # 루트 설명 파일
```

<br/>

## 🚀 주요 기능


| 기능                  | 설명                       |
|---------------------|--------------------------|
| `/agenda_generation/` | 	회의 주제 → 3~10개 회의 안건 자동 생성 |
| `/summarize/`         | 채팅 로그 기반 회의 요약 도출 |
| `/mbti_chat/`         | 참가자 MBTI에 기반한 챗봇 응답 생성 |

<br/>

## 🧪 실행 방법 (로컬)

```bash
# 의존성 설치
pip install -r requirements.txt

# .env 파일 생성
cp .env.template .env
# .env 내 GEMINI_API_KEY, MONGO_URI 등 설정

# 서버 실행
uvicorn Prompting.main:app --host 0.0.0.0 --port 8000
```

<br/>

## 🧩 향후 계획
- [ ] Prompting 기능 개선 (프롬프트 정제, 성능 평가)
- [ ] 전용 sLLM 도입 기반 로컬 모델 실험

<br/>

## 🧑‍💻 개발 문서 모음

| 위치                | 문서                                                      | 설명                        |
|-------------------|---------------------------------------------------------|---------------------------|
| `Prompting/`      | [`README.md`](./Prompting/README.md)                    | Prompting 모듈 소개           |
| `Prompting/docs/` | [`architecture.md`](./Prompting/docs/architecture.md)             | 전체 시스템 구성과 모듈 관계 설명       |
|                   | [`dataflow.md`](./Prompting/docs/dataflow.md)                     | 사용자의 요청 → 응답까지의 흐름 정리     |
|                   | [`prompting_strategy.md`](./Prompting/docs/prompting_strategy.md) | Gemini 프롬프팅 전략 가이드        |
|                   | [`api_spec.md`](./Prompting/docs/api_spec.md)                     | FastAPI 기반 API 명세서        |
|                   | [`GIT_GUIDE.md`](./Prompting/docs/GIT_GUIDE.md)                   | 브랜치 전략, 커밋 컨벤션, PR 작성 가이드 |
|                   | [`DEVELOPMENT_GUIDE.md`](./Prompting/docs/DEVELOPMENT_GUIDE.md)   | 코드 스타일, 예외 처리, 구조 설계 가이드  |


