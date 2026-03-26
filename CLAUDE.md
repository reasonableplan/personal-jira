# CLAUDE.md — Personal Jira 프로젝트

## 프로젝트 개요

Personal Jira는 AI 에이전트가 자율적으로 소프트웨어를 설계하고 개발할 수 있도록 지원하는 프로젝트 관리 플랫폼입니다.

**기술 스택:**
- **Frontend**: TypeScript + React 19 + Vite
- **Backend**: Python 3.11+ + FastAPI + SQLAlchemy
- **Database**: PostgreSQL 15
- **Containerization**: Docker + docker-compose

---

## 코딩 컨벤션

### Python (Backend)

#### 코드 스타일
- **Formatter**: Black
  - 라인 길이: 88자 (Black 기본값)
- **Import 정렬**: isort
  - 프로필: black (Black과 호환)
- **Linter**: Ruff
  - 설정: `ruff.toml` (프로젝트 루트)

#### 타입 힌팅 (필수)
```python
# ✅ Good
def get_project(project_id: str) -> Project:
    """프로젝트를 ID로 조회합니다."""
    pass

async def create_task(
    session: AsyncSession,
    task_data: TaskCreate,
) -> Task:
    """새로운 태스크를 생성합니다."""
    pass

# ❌ Bad
def get_project(project_id):  # 타입 없음
    pass
```

#### 에러 처리
- `Exception`을 받지 마세요 → 구체적인 예외 사용
- FastAPI의 `HTTPException` 사용
- 커스텀 예외는 `app/exceptions.py`에 정의

```python
# ✅ Good
try:
    project = await db.get(Project, project_id)
except NoResultFound:
    raise HTTPException(status_code=404, detail="Project not found")

# ❌ Bad
try:
    project = await db.get(Project, project_id)
except Exception:
    pass  # 예외 무시
```

#### 비동기 코드
- FastAPI는 **async-first** 프레임워크
- 모든 I/O 작업 (DB, API 호출)은 `async def` 사용
- `await` 필수 (기다림)
- DB 세션은 의존성 주입으로 전달

```python
# ✅ Good
@router.get("/projects/{id}")
async def get_project(
    id: str,
    session: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    project = await session.get(Project, id)
    return ProjectResponse.model_validate(project)

# ❌ Bad
@router.get("/projects/{id}")
def get_project(id: str):  # async 아님
    project = db.get(Project, id)  # 블로킹
    return project
```

#### 문서화 (Docstrings)
- 모든 함수/클래스에 docstring 작성 (Google 스타일)
- 한국어 또는 영어 (프로젝트에 통일)

```python
def create_project(
    name: str,
    description: str,
) -> Project:
    """새로운 프로젝트를 생성합니다.

    Args:
        name: 프로젝트 이름
        description: 프로젝트 설명

    Returns:
        생성된 Project 객체

    Raises:
        ValueError: name이 비어있으면 발생
    """
    if not name:
        raise ValueError("Project name cannot be empty")
    return Project(name=name, description=description)
```

### TypeScript/React (Frontend)

#### 코드 스타일
- **Formatter**: Prettier
  - 설정: `.prettierrc` (프로젝트 루트)
- **Linter**: ESLint + TypeScript strict mode
  - 설정: `tsconfig.json`의 `strict: true`

#### 타입 안전성 (필수)
```typescript
// ✅ Good
interface ProjectCreate {
  name: string;
  description: string;
}

const createProject = async (
  data: ProjectCreate
): Promise<Project> => {
  const response = await fetch("/api/projects", {
    method: "POST",
    body: JSON.stringify(data),
  });
  return response.json();
};

// ❌ Bad
const createProject = async (data: any) => {  // any 사용
  return fetch("/api/projects", { body: data });
};
```

#### React 컴포넌트
- 함수형 컴포넌트만 사용 (Hooks)
- Props는 interface로 정의

```typescript
// ✅ Good
interface ProjectCardProps {
  project: Project;
  onDelete?: (id: string) => void;
}

const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onDelete,
}) => {
  return <div>{project.name}</div>;
};

// ❌ Bad
const ProjectCard = ({ project, onDelete }: any) => {
  return <div>{project.name}</div>;
};
```

#### 상태 관리 (Zustand)
- Zustand store는 `src/stores/` 디렉토리
- 각 store는 도메인별로 분리 (projectStore, uiStore 등)

```typescript
// src/stores/projectStore.ts
import { create } from "zustand";

interface ProjectStore {
  projects: Project[];
  setProjects: (projects: Project[]) => void;
  addProject: (project: Project) => void;
}

export const useProjectStore = create<ProjectStore>((set) => ({
  projects: [],
  setProjects: (projects) => set({ projects }),
  addProject: (project) =>
    set((state) => ({
      projects: [...state.projects, project],
    })),
}));
```

#### API 클라이언트 (TanStack Query)
- 모든 서버 상태는 TanStack Query로 관리
- 쿼리/뮤테이션은 `src/api/` 디렉토리

```typescript
// src/api/projects.ts
import { useQuery, useMutation } from "@tanstack/react-query";

export const useProjects = () => {
  return useQuery({
    queryKey: ["projects"],
    queryFn: async () => {
      const response = await fetch("/api/projects");
      return response.json();
    },
  });
};

export const useCreateProject = () => {
  return useMutation({
    mutationFn: async (data: ProjectCreate) => {
      const response = await fetch("/api/projects", {
        method: "POST",
        body: JSON.stringify(data),
      });
      return response.json();
    },
    onSuccess: (data) => {
      console.log("Project created:", data);
    },
  });
};
```

---

## 커밋 메시지 형식

Conventional Commits 형식을 **반드시** 따릅니다.

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type (필수)
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포매팅 (Black, Prettier 등)
- `refactor`: 기능 변경 없는 코드 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드, 의존성 등 유지보수 작업
- `perf`: 성능 개선

### Scope (권장)
- `backend`, `frontend`, `db`, `docker`, `docs` 등

### Subject (필수)
- 명령형으로 시작 (Add, Fix, Refactor, 하지 않음: Added, Fixes)
- 영어 또는 한국어 (프로젝트에 통일)
- 마침표 없음
- 50자 이내

### Examples

```
feat(backend): Add project creation endpoint

fix(frontend): Fix broken responsive layout on mobile

docs(readme): Update installation instructions

refactor(backend): Extract database query logic into services

test(backend): Add unit tests for project validation

chore(docker): Update Python base image to 3.12
```

---

## 브랜치 네이밍

```
<type>/<task-id>-<short-desc>
```

### Format
- `type`: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- `task-id`: GitHub Issue / Linear ID (예: `#123`, `ENG-456`)
- `short-desc`: 하이픈으로 분리된 영어 소문자

### Examples
```
feat/123-user-authentication
fix/456-project-deletion-bug
docs/789-api-documentation
refactor/101-database-schema
```

### 보호된 브랜치
- `main`: 프로덕션 코드
  - PR 필수, 모든 체크 통과 필요
  - 최소 1명 리뷰 필수
- `develop`: 개발 브랜치
  - feature 브랜치에서 PR 제출

---

## Pull Request (PR) 규칙

### 제목 형식
```
[<scope>] <description>
```

Examples:
```
[Backend] Add project creation API endpoint
[Frontend] Fix responsive layout on mobile devices
[Docs] Update API documentation
```

### 설명 (Description)
```
## 변경 사항

- 프로젝트 생성 API 엔드포인트 추가
- 데이터베이스 마이그레이션 추가

## 테스트 방법

1. `POST /api/projects` 호출
2. 요청 본문: `{"name": "Test", "description": "..."}`
3. 응답: 201 + Project JSON

## Checklist

- [x] 로컬에서 테스트 완료
- [x] 린트 통과 (ruff, eslint)
- [x] 테스트 작성 및 통과
- [x] 문서 업데이트
```

### 자동 라벨링
PR은 변경된 파일 기준으로 자동 라벨이 추가됩니다:
- `backend/` 변경 → `backend` 라벨
- `frontend/` 변경 → `frontend` 라벨
- `docs/` 변경 → `documentation` 라벨

### CI/CD 체크 (필수 통과)
- ✅ Lint (Ruff for Python, ESLint for TypeScript)
- ✅ Type checking (mypy for Python, TypeScript compiler)
- ✅ Tests (pytest for Backend, vitest/jest for Frontend)
- ✅ Build (Backend: `pip install`, Frontend: `npm run build`)

---

## 테스트 커버리지 기준

### Backend (Python)
- **최소 기준**: 70% 커버리지
- **Target**: 80%+
- **도구**: pytest + pytest-cov

```bash
# 로컬 테스트 실행
cd backend
pytest

# 커버리지 리포트
pytest --cov=app tests/

# HTML 리포트 생성
pytest --cov=app --cov-report=html tests/
```

### Frontend (TypeScript/React)
- **최소 기준**: 60% 커버리지 (UI 컴포넌트 제외)
- **Target**: 70%+
- **도구**: Vitest + @vitest/coverage-v8

```bash
# 로컬 테스트 실행
cd frontend
npm run test

# 커버리지 리포트
npm run test:coverage
```

### 테스트 작성 규칙
- **Unit tests**: 비즈니스 로직, 유틸리티 함수
- **Integration tests**: API 엔드포인트, DB 쿼리
- **E2E tests**: 주요 사용자 시나리오 (향후)

```python
# Backend: conftest.py로 공유 fixture 정의
@pytest.fixture
async def test_db():
    """테스트용 데이터베이스 세션"""
    async with AsyncSession(...) as session:
        yield session

# Backend: test_projects.py
@pytest.mark.asyncio
async def test_create_project(test_db):
    """새 프로젝트 생성 테스트"""
    payload = {"name": "Test", "description": "..."}
    project = await create_project(test_db, payload)
    assert project.name == "Test"
```

---

## 에이전트별 역할 및 담당 디렉토리

### 1. Director Agent
- **역할**: 프로젝트 계획, 아키텍처 설계, 리뷰
- **담당 디렉토리**: None (크로스컷)
- **활동**:
  - 사용자와 대화로 요구사항 수집
  - 프로젝트 분해 및 태스크 생성
  - 다른 에이전트의 작업 리뷰

### 2. Backend Agent
- **역할**: API 및 비즈니스 로직 개발
- **담당 디렉토리**: `backend/app/`
- **활동**:
  - API 라우터 구현 (`routers/`)
  - 데이터 스키마 정의 (`schemas/`)
  - ORM 모델 작성 (`models/`)
  - 비즈니스 로직 구현 (`services/`)
  - DB 마이그레이션 추가 (`migrations/`)
  - 테스트 작성 (`tests/`)
- **금지**:
  - `frontend/` 디렉토리 수정
  - 환경설정 파일 (`.env`) 커밋

### 3. Frontend Agent
- **역할**: UI/UX 구현, 상태 관리, API 통합
- **담당 디렉토리**: `frontend/src/`
- **활동**:
  - React 컴포넌트 작성 (`components/`, `pages/`)
  - 상태 관리 스토어 작성 (`stores/`)
  - API 클라이언트 작성 (`api/`)
  - 타입 정의 (`types/`)
  - 테스트 작성 (`__tests__/`)
  - Vite 설정 업데이트 (필요시)
- **금지**:
  - `backend/` 디렉토리 수정
  - 타입스크립트 strict mode 완화

### 4. Git Agent
- **역할**: 저장소 및 브랜치 관리
- **담당 디렉토리**: None (Git 작업)
- **활동**:
  - 브랜치 생성/삭제
  - 커밋 메시지 작성 및 푸시
  - PR 생성 및 병합
  - 태그 관리
- **금지**:
  - 강제 푸시 (force push)
  - main 브랜치 직접 수정

### 5. Docs Agent
- **역할**: 문서 자동 생성 및 유지
- **담당 디렉토리**: `docs/`
- **활동**:
  - API 문서 자동 생성 (`API.md`)
  - 프로젝트 진행 상황 기록 (`work-log.md`)
  - 설정 가이드 작성 (`SETUP.md`)
  - README 업데이트
- **금지**:
  - 코드 작성
  - 설정 파일 수정

---

## 환경 설정

### 필수 환경변수

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/personal_jira

# FastAPI
DEBUG=False
SECRET_KEY=your-secret-key-here

# Claude API
CLAUDE_API_KEY=sk-...

# GitHub API (선택)
GITHUB_TOKEN=ghp_...
```

#### Frontend (.env.local)
```env
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=10000
```

### 설정 변경 시 동기화 필요
환경변수를 추가/변경하면:
1. `.env.example` 업데이트 (실제 값 제외)
2. `docker-compose.yml` 업데이트 (필요시)
3. `docs/SETUP.md` 업데이트

---

## 빌드 및 테스트

### 로컬 개발

#### Backend
```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행 (hot reload)
uvicorn app.main:app --reload

# 린트 및 타입 체크
ruff check .
mypy app/

# 테스트 실행
pytest
```

#### Frontend
```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 린트 및 타입 체크
npm run lint
npm run type-check

# 테스트 실행
npm run test

# 프로덕션 빌드
npm run build
```

### Docker로 실행

```bash
# 로컬 개발 환경 시작
docker-compose up -d

# 백엔드 서버 로그 확인
docker-compose logs -f backend

# 마이그레이션 실행
docker-compose exec backend alembic upgrade head

# 프론트엔드 접속
# http://localhost:5173

# 백엔드 API 접속
# http://localhost:8000
# http://localhost:8000/docs (Swagger UI)
```

---

## 주요 패턴 및 안티패턴

### ✅ Good Patterns

**의존성 주입 (Dependency Injection)**
```python
# FastAPI의 Depends를 사용한 DB 세션 주입
from fastapi import Depends
from app.database import get_db

@router.get("/projects")
async def list_projects(session: AsyncSession = Depends(get_db)):
    return await session.execute(select(Project))
```

**에러 처리 계층화**
```python
# Pydantic 검증 → 비즈니스 로직 에러 → HTTP 에러
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)  # Pydantic validation

async def create_project(session, data: ProjectCreate):
    if await project_exists(session, data.name):
        raise ValueError("Project already exists")  # Business logic error
    return await session.execute(...)
```

**TanStack Query 캐싱**
```typescript
// 자동 캐싱 및 백그라운드 리페치
const { data, isLoading, error } = useQuery({
  queryKey: ["projects"],
  queryFn: fetchProjects,
  staleTime: 5 * 60 * 1000,  // 5분 후 stale 됨
  gcTime: 10 * 60 * 1000,    // 10분 후 가비지 컬렉션
});
```

### ❌ Anti-patterns (금지)

**글로벌 상태 과다 사용**
```typescript
// ❌ 모든 상태를 Zustand에 저장
const useStore = create(state => ({
  projects: [],
  currentProject: null,
  selectedTask: null,
  filters: {},
  sorting: {},
  ...  // 100개의 상태
}));

// ✅ 서버 상태는 TanStack Query, 로컬 UI 상태만 Zustand
const useProjectStore = create(state => ({
  selectedFilters: {},
  sortBy: "name",
}));
```

**N+1 쿼리**
```python
# ❌ 나쁜 예: 루프에서 쿼리
for project_id in project_ids:
    project = await session.get(Project, project_id)  # N번의 쿼리

# ✅ 좋은 예: 한 번에 조회
stmt = select(Project).where(Project.id.in_(project_ids))
projects = await session.scalars(stmt)
```

**하드코딩된 설정값**
```python
# ❌ 나쁜 예
DATABASE_URL = "postgresql://localhost:5432/personal_jira"
API_TIMEOUT = 30

# ✅ 좋은 예 (app/config.py)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/personal_jira")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
```

---

## 검증 체크리스트

코드를 커밋하기 전에 반드시 확인하세요:

### Backend
- [ ] `ruff check backend/ --fix` 통과
- [ ] 타입 체크: `mypy app/`
- [ ] 테스트 통과: `pytest`
- [ ] 새로운 의존성은 `requirements.txt`에 추가
- [ ] 새로운 모델/스키마는 마이그레이션 생성
- [ ] 환경변수 추가 시 `.env.example` 업데이트

### Frontend
- [ ] `npm run lint` 통과
- [ ] 타입 체크: `npm run type-check`
- [ ] 테스트 통과: `npm run test`
- [ ] `npm run build` 성공
- [ ] 새로운 의존성은 `package.json`에 추가
- [ ] TypeScript strict mode 준수

### 모두
- [ ] 커밋 메시지 형식 준수
- [ ] 브랜치명 형식 준수
- [ ] `.gitignore`에 민감한 파일 포함되지 않음
- [ ] 문서 업데이트 (필요시)

---

## 연락처 및 문의

- **프로젝트 관리자**: (설정 필요)
- **Issue 트래킹**: GitHub Issues
- **문서**: `/docs/` 디렉토리

---

**마지막 업데이트**: 2026-03-27
