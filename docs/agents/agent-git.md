# Agent: Git/Infra — 전용 가이드

## 역할
Docker, CI/CD, Git 설정, 인프라 코드

## 작업 전 필수 읽기
1. `docs/ARCHITECTURE.md` — 프로젝트 구조
2. `docs/CONVENTIONS.md` — 규칙
3. `docs/agents/SHARED_LESSONS.md` — 공유 교훈
4. **이 파일**

## 작업 전 필수 확인
- `docker-compose.yml` 읽기 — 현재 서비스 구성
- `backend/Dockerfile`, `frontend/Dockerfile` 읽기
- `.env.example` 읽기 — 환경변수 목록

## 내 규칙
- Docker Compose: postgres port 5434, backend port 8000, frontend port 3000
- Dockerfile: multi-stage build, non-root user
- `.gitignore` 수정 시 `.worktrees/` 반드시 포함
- 환경변수 추가 시 `.env.example` 동기화

## Director 피드백 기록
<!-- Director가 reject할 때 아래에 추가 -->

