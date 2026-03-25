# Agent: Backend — 전용 가이드

## 역할
FastAPI + SQLAlchemy 기반 백엔드 API 구현

## 작업 전 필수 읽기
1. `docs/ARCHITECTURE.md` — 파일 트리, import 경로
2. `docs/CONVENTIONS.md` — 코딩 패턴
3. `docs/api-spec.md` — API 계약
4. `docs/agents/SHARED_LESSONS.md` — 공유 교훈
5. **이 파일**

## 작업 전 필수 확인
- `backend/app/main.py` 읽기 — 현재 등록된 라우터 확인
- `backend/app/models/__init__.py` 읽기 — 사용 가능한 모델 확인
- 기존 라우터 하나 읽기 (예: `routers/labels.py`) — 패턴 참고

## 내 규칙
- 모든 CRUD는 `api-spec.md` 엔드포인트/타입과 정확히 일치
- 새 라우터 만들면 `main.py`에 `include_router()` 추가
- 새 모델 만들면 `models/__init__.py`에 re-export 추가
- 서비스 클래스는 `GenericCRUDService` 상속 검토
- DB 작업은 `AsyncSession` + `select()` 패턴

## Director 피드백 기록
<!-- Director가 reject할 때 아래에 추가 -->

