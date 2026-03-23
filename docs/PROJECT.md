# Personal Jira 풀스택 시스템

## 프로젝트 개요
AI 에이전트 팀과 사람이 함께 사용하는 Jira 스타일 태스크 관리 시스템. FastAPI 백엔드 + React 프론트엔드 + PostgreSQL.

## 목적
AI 에이전트 팀(Director/Worker)과 사람(관리자)이 함께 사용하는 Jira 스타일 태스크 관리 시스템. 에이전트가 자동으로 태스크를 선점/처리하고, 사람이 대시보드로 모니터링/관리.

## 대상 사용자
Director 에이전트 (태스크 분배/리뷰), Worker 에이전트 (태스크 수행), 관리자(사람, 대시보드 모니터링)

## 범위
production-ready

## 기술 스택
- **frontend**: Vite, React 19, TypeScript, Tailwind CSS, Zustand, dnd-kit, TanStack Table
- **backend**: Python 3.12, FastAPI, SQLAlchemy, Alembic, asyncpg
- **database**: PostgreSQL 16
- **infra**: Docker Compose
- **etc**: uv, pnpm, pytest, vitest, WebSocket

## 설계 결정사항

- 백엔드 28개 기능 + 프론트엔드 16개 기능 전체 범위 확정
- 백엔드 우선 개발 → 프론트엔드 순서로 진행
- 프로젝트 구조: personal-jira/ (backend/ + frontend/ + docker-compose.yml)

## 제약사항

- 백엔드 API 먼저 만들고, 프론트엔드가 그 API를 참조
- Docker Compose로 PostgreSQL 사용
- 모든 기능에 테스트 필수



## Stories

### 프로젝트 인프라 및 환경 설정
Git 저장소, Docker Compose, 백엔드/프론트엔드 프로젝트 스캐폴딩, CI 기반 설정
- Sub-tasks: 4개

### 데이터베이스 스키마 및 모델
SQLAlchemy 모델 정의, Alembic 마이그레이션, 핵심 테이블 생성 (issues, comments, labels, dependencies, agents, sprints 등)
- Sub-tasks: 5개

### 기본 이슈 관리 API
이슈 CRUD, 타입/상태/우선순위 관리, 담당자 지정, 라벨 태깅, 코멘트 CRUD
- Sub-tasks: 6개

### 이슈 관계, 워크플로우, 검색 API
이슈 계층(Epic→Story→Task), 의존성 관계, 상태 워크플로우 전이, 검색/필터 API
- Sub-tasks: 4개

### 에이전트 특화 기능 API
자동 선점, 작업 로그, 실패/재시도, 코드 아티팩트, 자동 상태 전이, 리뷰 피드백 루프, 역량 매칭, 컨텍스트 번들, 시간 제한/자동 반납, 품질 메트릭
- Sub-tasks: 8개

### 추가 백엔드 기능 API
마일스톤/스프린트, 벌크 API, 활동 로그, 대시보드 통계, 알림 웹훅, 파일 첨부, 이슈 템플릿/복제
- Sub-tasks: 7개

### 실시간 통신 (WebSocket)
WebSocket 연결 관리, 이슈 상태 변경 실시간 브로드캐스트, 클라이언트 구독 관리
- Sub-tasks: 2개

### 프론트엔드 기반 설정 및 레이아웃
Vite+React 프로젝트 설정, Tailwind/다크모드, Zustand 스토어, API 클라이언트, 라우팅, 공통 레이아웃
- Sub-tasks: 4개

### 프론트엔드 핵심 뷰
칸반 보드(드래그&드롭), 테이블 뷰, 뷰 토글, 이슈 상세 사이드 패널, 이슈 생성/편집 폼, 마크다운 에디터
- Sub-tasks: 6개

### 프론트엔드 고급 기능
Epic 프로그레스 바, 대시보드 위젯/차트, 번다운 차트, 의존성 그래프, 타임라인/간트 차트, 검색 자동완성, 키보드 단축키, 토스트 알림, 실시간 WebSocket 연동
- Sub-tasks: 9개

### 통합 테스트 및 E2E
백엔드 통합 테스트, 프론트엔드 통합 테스트, 풀스택 E2E 시나리오 테스트
- Sub-tasks: 7개


---
> 이 파일은 Director Agent가 자동 생성합니다. 에이전트가 코드 생성 시 참조합니다.
