# ARCHITECTURE.md — Personal Jira MVP

> 프로젝트 디렉토리 구조, 주요 모듈, import 규칙, DB 스키마, 인프라 구성 문서.

---

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Backend | Python, FastAPI, SQLAlchemy, Alembic |
| Database | PostgreSQL (컨테이너: `agent-postgres`, port `5433`) |
| Infra | Docker Compose |

---

## 디렉토리 구조

```
project-root/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 앱 생성, 라우터 등록
│   │   ├── database.py          # DB 엔진, 세션 팩토리, get_db 의존성
│   │   ├── config.py            # 환경변수 설정 (Settings)
│   │   ├── models/              # SQLAlchemy ORM 모델
│   │   │   ├── __init__.py      # 모델 re-export
│   │   │   ├── epic.py
│   │   │   ├── story.py
│   │   │   ├── task.py
│   │   │   ├── label.py
│   │   │   └── task_label.py
│   │   ├── routers/             # FastAPI 라우터 (엔드포인트 정의)
│   │   │   ├── __init__.py
│   │   │   ├── epics.py
│   │   │   ├── stories.py
│   │   │   ├── tasks.py
│   │   │   └── labels.py
│   │   ├── schemas/             # Pydantic 요청/응답 스키마
│   │   │   ├── __init__.py
│   │   │   ├── epic.py
│   │   │   ├── story.py
│   │   │   ├── task.py
│   │   │   └── label.py
│   │   └── services/            # 비즈니스 로직 레이어
│   │       ├── __init__.py
│   │       ├── epic_service.py
│   │       ├── story_service.py
│   │       ├── task_service.py
│   │       └── label_service.py
│   ├── alembic/                 # DB 마이그레이션
│   │   ├── env.py
│   │   └── versions/
│   ├── tests/                   # 백엔드 테스트
│   │   ├── conftest.py
│   │   ├── test_epics.py
│   │   ├── test_stories.py
│   │   ├── test_tasks.py
│   │   └── test_labels.py
│   ├── alembic.ini
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # 재사용 가능한 UI 컴포넌트
│   │   │   ├── Button.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── StatusBadge.tsx
│   │   │   └── Layout.tsx
│   │   ├── pages/               # 라우트별 페이지 컴포넌트
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── KanbanPage.tsx
│   │   │   ├── EpicListPage.tsx
│   │   │   └── StoryDetailPage.tsx
│   │   ├── hooks/               # 커스텀 React 훅
│   │   │   ├── useEpics.ts
│   │   │   ├── useStories.ts
│   │   │   ├── useTasks.ts
│   │   │   └── useLabels.ts
│   │   ├── api/                 # API 클라이언트 (axios 기반)
│   │   │   ├── client.ts        # axios 인스턴스, baseURL 설정
│   │   │   ├── epics.ts
│   │   │   ├── stories.ts
│   │   │   ├── tasks.ts
│   │   │   └── labels.ts
│   │   ├── types/               # TypeScript 타입 정의
│   │   │   ├── epic.ts
│   │   │   ├── story.ts
│   │   │   ├── task.ts
│   │   │   └── label.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── package.json
│   └── Dockerfile
├── docs/
│   ├── ARCHITECTURE.md          # ← 이 파일
│   ├── PROJECT.md               # 프로젝트 개요, 스토리 목록
│   └── agents/                  # 에이전트 참조 문서
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 모듈 역할

### 백엔드 (`backend/app/`)

| 디렉토리 | 역할 | 예시 |
|-----------|------|------|
| `models/` | SQLAlchemy ORM 모델. 테이블 정의, 관계(relationship) 설정 | `Task` 모델에 `story_id` FK, `labels` M2M 관계 |
| `routers/` | FastAPI 라우터. HTTP 엔드포인트 정의, 요청 검증, 서비스 호출 | `POST /api/tasks` → `task_service.create_task()` |
| `schemas/` | Pydantic 스키마. 요청 body/응답 직렬화, 유효성 검증 | `TaskCreate`, `TaskResponse`, `TaskUpdate` |
| `services/` | 비즈니스 로직. DB 쿼리, 상태 전환 규칙, 복합 연산 | 태스크 상태 변경 시 유효성 검증 |

**데이터 흐름**: Router → Schema(검증) → Service(로직) → Model(DB) → Schema(응답)

### 프론트엔드 (`frontend/src/`)

| 디렉토리 | 역할 | 예시 |
|-----------|------|------|
| `components/` | 재사용 가능한 UI 컴포넌트. 상태 비의존적 | `Button`, `Modal`, `StatusBadge` |
| `pages/` | 라우트에 매핑되는 페이지 컴포넌트. 데이터 페칭 + 레이아웃 | `KanbanPage` — 칸반 보드 뷰 |
| `hooks/` | 커스텀 React 훅. API 호출 + 상태 관리 캡슐화 | `useTasks()` — 태스크 CRUD 훅 |
| `api/` | API 클라이언트. axios 인스턴스, 엔드포인트별 함수 | `getTasks()`, `createTask()` |
| `types/` | TypeScript 타입/인터페이스 정의 | `Task`, `Epic`, `Story` 인터페이스 |

---

## Import 경로 규칙

### 백엔드 (Python) — 절대 경로

```python
# 모델
from app.models.task import Task
from app.models import Task  # __init__.py에서 re-export

# 스키마
from app.schemas.task import TaskCreate, TaskResponse

# 서비스
from app.services.task_service import create_task

# DB 세션
from app.database import get_db

# 설정
from app.config import settings
```

### 프론트엔드 (TypeScript) — `@/` alias

```typescript
// vite.config.ts에서 @ → src/ 매핑
import { Button } from '@/components/Button'
import { useTasks } from '@/hooks/useTasks'
import { getTasks } from '@/api/tasks'
import type { Task } from '@/types/task'
```

`vite.config.ts` alias 설정:
```typescript
resolve: {
  alias: {
    '@': path.resolve(__dirname, './src'),
  },
}
```

---

## 라우터 목록

| 라우터 파일 | prefix | 주요 엔드포인트 |
|-------------|--------|-----------------|
| `routers/epics.py` | `/api/epics` | CRUD — 목록, 생성, 조회, 수정, 삭제 |
| `routers/stories.py` | `/api/stories` | CRUD — 에픽 내 스토리 관리 |
| `routers/tasks.py` | `/api/tasks` | CRUD + 상태 전환, 필터/검색 |
| `routers/labels.py` | `/api/labels` | CRUD + 태스크-라벨 연결/해제 |

`main.py` 등록 패턴:
```python
from app.routers import epics, stories, tasks, labels

app.include_router(epics.router)
app.include_router(stories.router)
app.include_router(tasks.router)
app.include_router(labels.router)
```

---

## DB 스키마 개요

### 테이블 관계도

```mermaid
erDiagram
    epics ||--o{ stories : "1:N"
    stories ||--o{ tasks : "1:N"
    tasks ||--o{ task_labels : "1:N"
    labels ||--o{ task_labels : "1:N"

    epics {
        uuid id PK
        varchar title
        text description
        varchar status
        timestamp created_at
        timestamp updated_at
    }

    stories {
        uuid id PK
        uuid epic_id FK
        varchar title
        text description
        varchar status
        int priority
        timestamp created_at
        timestamp updated_at
    }

    tasks {
        uuid id PK
        uuid story_id FK
        varchar title
        text description
        varchar status
        int priority
        timestamp created_at
        timestamp updated_at
    }

    labels {
        uuid id PK
        varchar name
        varchar color
        timestamp created_at
    }

    task_labels {
        uuid task_id FK
        uuid label_id FK
    }
```

### 테이블 관계 요약

```
epics (1) ──→ (N) stories (1) ──→ (N) tasks
                                        │
                                   task_labels (M:N 연결 테이블)
                                        │
                                      labels
```

- **epics → stories**: 하나의 에픽에 여러 스토리 (`stories.epic_id` FK)
- **stories → tasks**: 하나의 스토리에 여러 태스크 (`tasks.story_id` FK)
- **tasks ↔ labels**: 다대다 관계, `task_labels` 연결 테이블 (`task_id`, `label_id` 복합 PK)

### 상태(status) 값

| 엔티티 | 가능한 상태 |
|--------|------------|
| Epic | `planning`, `active`, `done` |
| Story | `todo`, `in_progress`, `done` |
| Task | `todo`, `in_progress`, `in_review`, `done` |

---

## Docker Compose 서비스 구성

```yaml
services:
  postgres:
    image: postgres:16
    container_name: agent-postgres
    ports:
      - "5433:5432"
    environment:
      POSTGRES_DB: agent_db
      POSTGRES_USER: agent
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://agent:${POSTGRES_PASSWORD}@postgres:5432/agent_db
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
```

### 서비스 요약

| 서비스 | 포트 | 설명 |
|--------|------|------|
| `postgres` | `5433` (호스트) → `5432` (컨테이너) | PostgreSQL 16, 컨테이너명 `agent-postgres` |
| `backend` | `8000` | FastAPI 서버, DB 의존 |
| `frontend` | `5173` | Vite dev 서버, 백엔드 의존 |

---

## 의존성 순서

```
문서(docs) → DB/모델(models) → API(routers) → 프론트엔드(frontend)
```

프론트엔드는 백엔드 API 완성 후 시작. 각 레이어는 하위 레이어에만 의존한다.
<!-- AUTO-UPDATED -->
## 자동 갱신 (2026-03-26 03:54 UTC)

### 등록된 라우터 (main.py)
- 없음

### 모델 exports (models/__init__.py)
- 없음
