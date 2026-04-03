# Project Skeleton — Personal Jira

> 이 파일은 프로젝트 계약서. 전체 템플릿: docs/skeleton_template.md 참조.
> Architect/Designer가 나머지 섹션을 채운다.

## 1. Overview
- **프로젝트명**: Personal Jira
- **한 줄 설명**: AI agent team and human PM issue tracking system
- **목적**: Task management tool for agent orchestration. Agents auto-create/assign/manage issues, PM monitors progress in real-time
- **타겟 사용자**: AI agents (architect, designer, orchestrator, backend_coder, frontend_coder, reviewer, qa) + Human (PM)

## 2. 기능 요구사항

### 핵심 기능 (MVP)
- [x] Issue CRUD (title, description, priority, labels, assignee)
- [x] Kanban board (TODO → IN_PROGRESS → REVIEW → DONE)
- [x] Sprint management (create, assign issues, start/complete)
- [x] Comments system
- [x] Assignee management (agent auto-assign + manual)
- [x] Filter/search (status, assignee, label, priority)
- [x] Auto task assignment — Orchestrator assigns by agent capability
- [x] Skeleton integration — issue links to skeleton section reference (e.g. "skeleton §7 GET /api/issues")
- [x] PR auto-link — auto-link PR when Coder creates one
- [x] Agent execution log — per-issue attempt count, token usage, duration
- [x] Reject history — Reviewer reject reasons + Coder retry records auto-accumulated
- [x] Dependency graph — blocking relationships between issues
- [x] Agent dashboard view — per-agent "my tasks" / "completed" / "rejected" filter
- [x] Auto status transition — branch create→IN_PROGRESS, PR→REVIEW, merge→DONE

### 추가 기능 (후순위)
- [ ] Agent performance analytics (completion rate, avg duration, reject ratio)
- [ ] Email/Slack notifications
- [ ] Dark mode
- [ ] Issue templates
- [ ] Bulk operations (multi-issue status change)

## 3. 기술 스택

### 프론트엔드 (TypeScript)
- **프레임워크**: React
- **상태 관리**: Zustand
- **서버 상태**: TanStack Query (React Query)
- **HTTP 클라이언트**: axios
- **스타일링**: Tailwind CSS + CSS Modules
- **폼**: React Hook Form
- **라우팅**: React Router
- **UI 컴포넌트**: shadcn/ui

### 백엔드 (Python)
- **프레임워크**: FastAPI
- **ORM**: SQLModel
- **마이그레이션**: Alembic
- **인증**: python-jose (JWT) + passlib
- **유효성 검증**: Pydantic
- **테스트**: pytest + httpx
- **DB**: PostgreSQL

## 4~19. (Architect/Designer가 채울 섹션)

> skeleton_template.md의 섹션 4~19 구조를 따른다.
> Architect: 섹션 5(인증), 6(DB), 7(API), 9(에러), 10(상태흐름) 작성
> Designer: 섹션 8(UI/UX) 작성
> Orchestrator: 섹션 17(태스크 분해) 작성
