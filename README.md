# Personal Jira MVP

Epic / Story / Task 기반의 경량 프로젝트 관리 도구.

## 기술 스택

| 레이어 | 기술 |
|--------|------|
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Backend | Python, FastAPI, SQLAlchemy, Alembic |
| Database | PostgreSQL 16 |
| Infra | Docker Compose |

## 아키텍처 개요

```mermaid
flowchart LR
    Browser -->|HTTP| Frontend
    Frontend -->|REST API| Backend
    Backend -->|SQL| PostgreSQL

    subgraph Docker Compose
        Frontend
        Backend
        PostgreSQL
    end
```

**백엔드 요청 흐름**: Router → Schema(검증) → Service(로직) → Model(DB) → Schema(응답)

## 디렉토리 구조

```
project-root/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 앱, 라우터 등록
│   │   ├── database.py      # DB 엔진, 세션, get_db
│   │   ├── config.py        # 환경변수 설정
│   │   ├── models/          # SQLAlchemy ORM 모델
│   │   ├── routers/         # FastAPI 라우터
│   │   ├── schemas/         # Pydantic 스키마
│   │   └── services/        # 비즈니스 로직
│   ├── alembic/             # DB 마이그레이션
│   ├── tests/               # pytest 테스트
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # 재사용 UI 컴포넌트
│   │   ├── pages/           # 라우트별 페이지
│   │   ├── hooks/           # 커스텀 React 훅
│   │   ├── api/             # API 클라이언트 (axios)
│   │   └── types/           # TypeScript 타입
│   ├── package.json
│   └── Dockerfile
├── docs/                    # 프로젝트 문서
├── docker-compose.yml
├── .env.example
└── README.md
```

## 로컬 개발 환경 설정

### 사전 요구사항

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- Git

### 1. 저장소 클론

```bash
git clone <repository-url>
cd personal-jira
```

### 2. 환경변수 설정

```bash
cp .env.example .env
```

`.env.example`에 기본값이 포함되어 있어 로컬 개발 시 별도 수정 없이 사용 가능합니다.

### 3. Docker Compose 실행

```bash
docker compose up -d
```

| 서비스 | URL | 설명 |
|--------|-----|------|
| Backend | `http://localhost:8000` | FastAPI 서버 (auto-reload) |
| Frontend | `http://localhost:5173` | Vite 개발 서버 |
| PostgreSQL | `localhost:5433` | DB (호스트 포트 5433 → 컨테이너 5432) |

### 4. DB 마이그레이션

```bash
docker compose exec backend alembic upgrade head
```

### 5. API 문서 확인

FastAPI가 자동 생성하는 API 문서:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 환경변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `DATABASE_URL` | SQLAlchemy 연결 문자열 | `postgresql://postgres:postgres@localhost:5433/personal_jira` |
| `POSTGRES_USER` | PostgreSQL 사용자명 | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL 비밀번호 | `postgres` |
| `POSTGRES_DB` | 데이터베이스명 | `personal_jira` |
| `BACKEND_PORT` | FastAPI 서버 포트 | `8000` |
| `FRONTEND_PORT` | Vite 개발 서버 포트 | `5173` |
| `APP_ENV` | 애플리케이션 환경 | `development` |
| `SECRET_KEY` | JWT/세션 서명 키 | `change-me-in-production` |

## 개발 명령어

```bash
# 전체 서비스 시작
docker compose up -d

# 로그 확인
docker compose logs -f backend

# 서비스 중지
docker compose down

# DB 초기화 (볼륨 삭제)
docker compose down -v
```

## 프로젝트 문서

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — 아키텍처, DB 스키마, 모듈 구조
- [CONVENTIONS.md](docs/CONVENTIONS.md) — 코딩 규칙, 네이밍, Git 워크플로우

## 라이선스

Private — 내부 사용 전용
