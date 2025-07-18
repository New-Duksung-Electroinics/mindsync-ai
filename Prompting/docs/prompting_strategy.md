# ✨ Prompting 전략 가이드

> 이 문서는 Gemini API를 사용할 때의 프롬프트 구성 방식과 설계 전략을 기록합니다.

<br/>

## 1. 프롬프트 설계 철학

- **Context 우선 구성**: 회의 맥락을 충분히 전달
- **Role 지정 강조**: Gemini에게 역할을 명확히 설명
- **다국어 실험**: 한/영 프롬프트 비교 테스트 진행

<br/>

## 2. 주요 프롬프트 유형

### ✅ 회의 안건 생성
- 입력: 사용자의 주제 요청
- 출력: 3~10개의 JSON 형식 안건 리스트
- 구조화된 응답을 위해 `response_schema` 지정



### ✅ 회의 요약
- 입력: 주제, 안건, 채팅 기록 (context chunk)
- 출력: 각 안건별 발언 요약 + 결론
- 입력 토큰 제한에 걸릴 시 분할된 context chunks 전달 (Gemini의 입력 토큰 limit을 고려했을 때 가능성 희박)



### ✅ MBTI 챗봇
- 입력: 챗봇의 MBTI 유형, 주제, 직전 채팅 로그
- 출력: 새로운 안건으로 넘어가는 시점에서 성향에 맞는 자연스러운 발언

<br/>

## 3. 토큰 수 제한 처리 전략

- context가 너무 길어질 경우, 토큰 수 기준으로 분할
- 각 chunk 단위로 프롬프트를 나눠 Gemini에 전송 (비동기 병렬 처리)

<br/>

## 4. 향후 개선 고려

- 프롬프트 템플릿 언어/지시 방식/응답 형식 구조에 따른 성능 실험 및 개선 방안 모색
- 기능별 프롬프트 구성 전략 세분화/구체화
- 피드백 기반 프롬프트 조정 가능성
