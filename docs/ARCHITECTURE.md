# Personal Jira — Architecture (자동 갱신됨)

> 이 문서는 merge 후 자동 갱신됩니다. 코드 작성 전 반드시 읽으세요.

## 프로젝트 구조

```
backend/
  app/
    main.py              — FastAPI 앱 (라우터 등록, 미들웨어)
    config.py            — Settings (pydantic-settings)
    database.py          — AsyncSession, get_db(), Base, engine
    exceptions.py        — NotFoundError, ConflictError, register_exception_handlers()
    models/
      __init__.py        — 모든 모델 re-export
      base.py            — Base(DeclarativeBase) 만 정의
      issue.py           — Epic, Story, Task, Label, task_labels(Table)
    routers/             — FastAPI APIRouter 모듈들
      labels.py          — /api/labels CRUD
    schemas/             — Pydantic 요청/응답 모델
      common.py          — PaginatedResponse, ErrorResponse, PaginationParams
      label.py           — LabelCreate, LabelUpdate, LabelResponse
    services/            — 비즈니스 로직
      base.py            — GenericCRUDService (제네릭 CRUD)
      label.py           — LabelService
  alembic/               — DB 마이그레이션
    versions/0001_initial_schema.py
  tests/                 — pytest 테스트
frontend/
  src/
    api/client.ts        — apiClient (fetch wrapper)
    App.tsx              — 라우팅 설정
    main.tsx             — React 진입점
    components/          — 공통 컴포넌트
    pages/               — 페이지 컴포넌트 (stub 상태)
    types/index.ts       — TypeScript 타입 정의
docs/
  api-spec.md            — API 계약 (엔드포인트, 타입)
  ARCHITECTURE.md        — 이 파일
  CONVENTIONS.md         — 코딩 규칙
docker-compose.yml       — postgres + backend + frontend
```

## 핵심 import 경로

```python
# 모델 — 반드시 app.models에서 import (app.models.base 아님!)
from app.models import Epic, Story, Task, Label, task_labels

# DB 세션
from app.database import get_db, Base, engine, async_session_factory

# 설정
from app.config import settings

# 예외
from app.exceptions import NotFoundError, ConflictError

# 스키마
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.label import LabelCreate, LabelUpdate, LabelResponse
```

## 새 기능 추가 시 반드시 할 것

### 새 라우터 추가
1. `backend/app/routers/{name}.py` 생성
2. `backend/app/main.py`에 등록:
```python
from app.routers.{name} import router as {name}_router
app.include_router({name}_router, prefix="/api")
```

### 새 모델 추가
1. `backend/app/models/issue.py`에 클래스 추가
2. `backend/app/models/__init__.py`에 re-export 추가
3. alembic 마이그레이션 생성

### 새 디렉토리 생성 시
- `__init__.py` 반드시 생성 (빈 파일이라도)

## DB 테이블 (마이그레이션 기준)

| 테이블 | ORM 모델 | 상태 |
|--------|----------|------|
| epics | Epic | ✅ |
| stories | Story | ✅ |
| tasks | Task | ✅ |
| labels | Label | ✅ |
| task_labels | task_labels (Table) | ✅ (association) |
| activities | ❌ 미구현 | 모델 필요 |
| agents | ❌ 미구현 | 모델 필요 |

## 현재 등록된 라우터

| prefix | 라우터 | 등록 여부 |
|--------|--------|----------|
| /health | main.py 직접 | ✅ |
| /api/labels | routers/labels.py | ❌ main.py에 미등록 |
| /api/epics | 미구현 | ❌ |
| /api/stories | 미구현 | ❌ |
| /api/tasks | 미구현 | ❌ |
| /api/board | 미구현 | ❌ |
| /api/agents | 미구현 | ❌ |
