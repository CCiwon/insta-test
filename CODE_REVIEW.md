# Code Review: Instagram AI Agent

**Date**: 2026-03-20
**Reviewer**: Claude Code
**Verdict**: BLOCK — CRITICAL issues must be resolved before production deployment

---

## 🔴 CRITICAL (즉시 수정 필요)

### 1. `/publish/*` 엔드포인트 인증 없음
**File**: `app/routes/publish.py:16-58`

`/publish/feed`, `/publish/story` 엔드포인트에 인증이 전혀 없습니다.
URL을 아는 사람은 누구든 인스타그램 계정에 게시물을 올릴 수 있습니다.

**Fix**: `ADMIN_API_KEY` 환경변수 기반 Bearer Token 인증 추가

---

### 2. Access Token이 URL 쿼리 파라미터에 노출
**File**: `app/services/instagram_publish_service.py:44-46, 62-64`

`access_token`이 `params=`로 전달되어 URL 쿼리스트링에 포함됩니다.
서버 로그, 프록시 로그, CDN 로그에 토큰이 평문으로 남습니다.

**Fix**: `data=` (POST body form-encoded)로 전환하여 URL에서 제거

---

### 3. Path Traversal / SSRF 취약점
**File**: `app/services/media_service.py:11`

`override_filename`이 검증 없이 URL에 삽입됩니다.
`../../etc/passwd` 같은 입력으로 SSRF 공격에 악용될 수 있습니다.

**Fix**: 파일명을 `^[a-zA-Z0-9_\-]+\.[a-zA-Z0-9]+$` 정규식으로 검증

---

### 4. Prompt Injection 취약점
**File**: `app/prompts/reply_prompt.py:29`, `app/services/comment_service.py:62`

댓글 텍스트가 GPT 프롬프트에 직접 삽입됩니다.
악성 유저가 `"Ignore all previous instructions..."` 같은 댓글로 AI 응답을 조작할 수 있습니다.

**Fix**: 댓글 텍스트 최대 500자 제한 + 프롬프트 구분자 이스케이프 처리

---

## 🟠 HIGH (조속히 수정)

### 5. 웹훅 처리가 동기적 — 5초 타임아웃 위험
**File**: `app/routes/webhook.py:103-108`

Instagram은 5초 내 200 응답이 없으면 재전송합니다.
GPT API 호출이 5초를 넘기면 같은 댓글이 중복 처리됩니다.
comment_id 기반 중복 제거(idempotency) 로직도 없습니다.

**Fix**: FastAPI `BackgroundTasks`로 비동기 처리 + comment_id dedup

---

### 6. 내부 에러 정보가 클라이언트에 노출
**File**: `app/routes/publish.py:29, 51`

`detail=f"Feed publish failed: {e}"` 형태로 예외 메시지가 그대로 반환됩니다.
스택 트레이스, 내부 서비스 정보가 외부에 노출될 수 있습니다.

**Fix**: 클라이언트에는 generic 메시지만, 상세 정보는 로그에만 남기기

---

### 7. `requirements.txt` 구조 문제
**File**: `requirements.txt:5, 9`

- `httpx==0.27.2` 중복 등재
- 테스트 의존성(`pytest`, `pytest-asyncio`)이 프로덕션 의존성과 혼재

**Fix**: 중복 제거, `requirements-dev.txt`로 테스트 의존성 분리

---

### 8. 모듈 레벨 서비스 전역 인스턴스화
**File**: `app/routes/publish.py:11-13`, `app/services/comment_service.py:9`

서비스가 모듈 import 시점에 인스턴스화됩니다.
설정이 import 전에 준비되어야 하고, 테스트 격리가 어렵습니다.

**Fix**: FastAPI Dependency Injection 패턴 적용

---

## 🟡 MEDIUM (이번 주 내 수정)

| # | 위치 | 이슈 |
|---|------|------|
| 9 | `app/main.py` | 모든 엔드포인트에 Rate Limiting 없음 |
| 10 | `instagram_publish_service.py:77` | 재시도마다 새 `httpx.AsyncClient` 생성, 지수 백오프 없음 |
| 11 | `gpt_service.py:33-37` | GPT 응답 파싱이 줄바꿈 기반으로 취약, 3개 미만 반환 시 처리 없음 |
| 12 | `routes/webhook.py:84` | 서명 헤더값이 실패 로그에 기록됨 |
| 13 | `app/main.py:36` | `StaticFiles(directory="app/static")` 상대 경로 사용 |
| 14 | `app/main.py` | CORS 미들웨어 없음 |
| 15 | `tests/` | `InstagramPublishService`, `MediaService` 테스트 부재 |
| 16 | `app/main.py:42` | `/health` 엔드포인트가 `env` 정보를 인증 없이 노출 |

---

## 💡 SUGGESTIONS (낮은 우선순위)

| # | 이슈 |
|---|------|
| 17 | 반환 타입을 `dict` 대신 `TypedDict`로 명시 |
| 18 | 스팸/비속어 단어 목록을 코드가 아닌 설정 파일로 관리 |
| 19 | 댓글 텍스트 최대 길이 제한 없음 (OpenAI 토큰 비용 과다) |
| 20 | `StaticFiles` 절대 경로 사용 권장 (`Path(__file__).parent`) |

---

## 수정 이력

| 날짜 | 수정 항목 | 상태 |
|------|----------|------|
| 2026-03-20 | CRITICAL #1: publish 인증 추가 | ✅ 완료 |
| 2026-03-20 | CRITICAL #2: access_token URL 노출 제거 | ✅ 완료 |
| 2026-03-20 | CRITICAL #3: path traversal 방어 | ✅ 완료 |
| 2026-03-20 | CRITICAL #4: prompt injection 방어 | ✅ 완료 |
