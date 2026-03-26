# Agent: Git

> Git/CI 워크플로우 및 인프라 관리 전담 에이전트 가이드.

---

## 역할 요약

- **담당**: Git 워크플로우, CI/CD, Docker Compose 관리
- **업무**: 브랜치 전략 실행, PR 관리, 커밋 규칙 적용, Docker 서비스 구성
- **목표**: 일관된 Git 히스토리 유지, 안정적인 빌드/배포 파이프라인 운영

---

## 담당 디렉토리 및 파일

```
project-root/
├── .gitignore               # Git 추적 제외 규칙
├── docker-compose.yml       # Docker 서비스 구성
├── backend/
│   └── Dockerfile           # 백엔드 Docker 이미지
├── frontend/
│   └── Dockerfile           # 프론트엔드 Docker 이미지
└── .github/                 # GitHub Actions (CI/CD)
    └── workflows/
```

---

## 참조 문서

| 문서 | 용도 |
|------|------|
| `docs/CONVENTIONS.md` | 커밋 메시지 규칙, 브랜치 네이밍, Git 워크플로우 |
| `docs/ARCHITECTURE.md` | Docker Compose 서비스 구성, 포트 매핑 |
| `docs/agents/SHARED_LESSONS.md` | 과거 실수 및 금지사항 |

---

## 코딩 규칙

### 커밋 메시지: Conventional Commits

```
<type>: <description>

[optional body]
```

| type | 용도 |
|------|------|
| `feat` | 새 기능 |
| `fix` | 버그 수정 |
| `docs` | 문서 변경 |
| `test` | 테스트 추가/수정 |
| `refactor` | 기능 변경 없는 코드 개선 |
| `chore` | 빌드, 의존성, 설정 변경 |

**예시:**

```
feat: 태스크 라벨 CRUD API 추가
fix: 에픽 삭제 시 하위 스토리 cascade 누락 수정
docs: ARCHITECTURE.md DB 스키마 섹션 추가
test: 태스크 상태 전환 엣지 케이스 테스트 추가
chore: Docker Compose PostgreSQL 버전 업그레이드
```

### 브랜치 전략

```mermaid
gitgraph
    commit id: "main"
    branch feat/task-labels-api
    commit id: "feat: 라벨 모델 추가"
    commit id: "feat: 라벨 CRUD API"
    commit id: "test: 라벨 API 테스트"
    checkout main
    merge feat/task-labels-api id: "PR #12 merge"
```

#### 브랜치 네이밍

```
<type>/<short-description>
```

| 예시 | 설명 |
|------|------|
| `feat/task-labels-api` | 태스크 라벨 API 기능 추가 |
| `fix/epic-cascade-delete` | 에픽 삭제 cascade 버그 수정 |
| `docs/conventions-md` | CONVENTIONS.md 문서 작업 |
| `chore/docker-compose-update` | Docker 설정 변경 |

#### 규칙

- `main` 브랜치에 직접 push 금지 — PR을 통해서만 머지
- 브랜치명은 영문 소문자, 하이픈(`-`) 구분
- 하나의 브랜치 = 하나의 작업 단위 (feature, fix, etc.)

### PR 규칙

| 항목 | 규칙 |
|------|------|
| 제목 | Conventional Commits 형식 (`feat: ...`, `fix: ...`) |
| 본문 | 변경 사항 요약, 테스트 계획 포함 |
| 리뷰 | 머지 전 최소 1명 리뷰 (자동화 에이전트 포함) |
| CI | 모든 CI 체크 통과 필수 |
| 충돌 | 머지 전 충돌 해결 필수 |

### Docker Compose 관리

#### 서비스 구성

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

#### 포트 매핑

| 서비스 | 호스트 포트 | 컨테이너 포트 |
|--------|------------|--------------|
| `postgres` | `5433` | `5432` |
| `backend` | `8000` | `8000` |
| `frontend` | `5173` | `5173` |

#### 의존성 순서

```mermaid
flowchart LR
    A[postgres] --> B[backend]
    B --> C[frontend]
```

### .gitignore 관리

프로젝트에 필수 제외 항목:

```
# Python
__pycache__/
*.pyc
.venv/
*.egg-info/

# Node
node_modules/
dist/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/

# DB
*.db
*.sqlite3

# Docker
postgres_data/
```

---

## 테스트 요구사항

### CI 파이프라인 검증

| 검증 항목 | 명령어 |
|-----------|--------|
| 백엔드 lint | `ruff check backend/ --config ruff.toml` |
| 백엔드 테스트 | `pytest backend/tests/` |
| 백엔드 import 확인 | `python -c "from app.main import app"` |
| 프론트엔드 lint | `npx eslint src/` |
| 프론트엔드 타입 체크 | `npx tsc --noEmit` |
| 프론트엔드 테스트 | `npx vitest run` |
| Docker 빌드 | `docker compose build` |

### Docker 동작 검증

```
[ ] docker compose build — 이미지 빌드 성공
[ ] docker compose up -d — 모든 서비스 정상 기동
[ ] postgres 컨테이너 헬스 체크 통과
[ ] backend 서비스가 postgres에 연결 성공
[ ] frontend 서비스가 backend에 연결 성공
[ ] docker compose down — 정상 종료
```

### Git 히스토리 검증

```
[ ] 커밋 메시지가 Conventional Commits 형식
[ ] 브랜치명이 <type>/<description> 형식
[ ] main 브랜치에 직접 커밋 없음
[ ] 머지 커밋이 PR 번호 포함
```

---

## 금지사항

- `main` 브랜치에 직접 push 금지
- `--force` push 금지 (히스토리 파괴)
- `.git/` 디렉토리 직접 조작 금지
- 시크릿/토큰을 커밋에 포함 금지 — 환경변수 사용
- `.env` 파일 커밋 금지 — `.env.example`만 커밋
- Docker 이미지에 시크릿 하드코딩 금지 — 환경변수 주입
- CI 체크 미통과 상태에서 머지 금지
- 의미 없는 커밋 메시지 금지 (`fix`, `update`, `wip` 등)
