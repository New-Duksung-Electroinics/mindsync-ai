# 🌿 Git 전략 가이드

> 이 문서는 MindSync AI 백엔드 모듈(Prompting)의 Git 브랜치 전략, 커밋 컨벤션, PR 가이드에 대한 내용을 다룹니다.
>
> 📅 작성일: 2025.04.08  
> ⏳ 적용 기간: 2025.04.08 - (추후 변경 가능)

<br/>

## 𖦥 브랜치 전략

### 기본 브랜치
- `main`: 배포용 브랜치 (CI/CD가 연결된 안정된 코드)
- `dev`: 통합 개발 브랜치 (기능 개발/수정은 이 브랜치로 PR 병합 + hotfix는 직접 push 가능)

### 작업 브랜치 네이밍 규칙
| prefix | 설명 | 예시 |
|--------|------|------|
| `feature/` | 신규 기능 추가 | `feature/agenda-generation` |
| `refactor/` | 리팩토링 작업 | `refactor/services-core` |
| `fix/` | 버그 수정 | `fix/chat-timestamp-bug` |
| `docs/` | 문서 관련 | `docs/api-spec` |

> 브랜치는 `dev`로부터 생성하고, 작업 완료 후 `dev`로 PR

<br/>

## 💬 커밋 메시지 컨벤션

- 기본 형식: `타입: 작업 요약` (선택적으로 이슈 번호 첨부)

### 커밋 타입
| 타입 | 설명 |
|------|------|
| `feat` | 기능 추가 |
| `fix` | 버그 수정 |
| `refactor` | 코드 리팩토링 (기능 변화 없음) |
| `docs` | 문서 수정 |
| `chore` | 설정 변경, 패키지 관리 등 |
| `test` | 테스트 코드 추가 |

### 예시
```bash
git commit -m "feat: 회의 요약 생성 기능 구현"
git commit -m "refactor: GeminiClient 상수 및 구조 개선"
```

<br/>

## 📌 PR 가이드

### PR 제목
`태그: 작업 요약`

예:
```
Refactor: services 리팩토링
Feature: 안건 자동 생성 기능 추가
```

### PR 본문 예시
```markdown
## 개요
Gemini 기반 서비스 객체 내부 구조를 개선하고 템플릿/컨텍스트 관리 방식 리팩토링

## 주요 변경 사항
- GeminiClient: 기본 모델 상수화, 토큰 수 계산 개선
- 서비스 객체 내부 템플릿 추출
- context_builders 패키지 도입 및 로직 분리
- usecase 제거 및 서비스 책임 명확화

## 테스트/검토 사항
- [x] 모든 endpoint 테스트 완료
```

### 체크리스트
- [x] 로컬 테스트 완료
- [x] 충돌 없음 확인
- [x] 관련 이슈/기능 설명 포함

<br/>

## 🧪 추천 워크플로우

```bash
git checkout dev
git pull origin dev
git checkout -b refactor/services-core

# 작업 후 커밋/푸시

git push origin refactor/services-core
# GitHub에서 dev로 PR 생성 및 리뷰
```

> `dev`로의 PR 병합은 **Squash and Merge**, `main`으로의 PR 병합은 **Rebase and Merge** 권장

