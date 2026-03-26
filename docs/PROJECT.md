# Personal Jira MVP

## 프로젝트 개요
에픽>스토리>태스크 3단 계층, 칸반 보드, 대시보드를 갖춘 개인용 프로젝트/할일 관리 웹앱 MVP 개발

## 목적
개인 프로젝트와 할일을 Jira처럼 체계적으로 관리. 에픽>스토리>태스크 계층, 칸반 보드, 대시보드 제공

## 대상 사용자
본인 1인 사용 (개인용)

## 범위
MVP — 2주 내 핵심 기능 동작, 테스트 필수 작성

## 기술 스택
- **frontend**: React, TypeScript, Vite, Tailwind CSS
- **backend**: Python, FastAPI, SQLAlchemy, Alembic
- **database**: PostgreSQL (agent-postgres 컨테이너, port 5433)
- **infra**: Docker Compose

## 설계 결정사항

- 기술 스택 확정: FastAPI+SQLAlchemy / React+TS+Vite+Tailwind / PostgreSQL(5433) / Docker Compose
- 의존성 순서 확정: 문서 → DB/모델 → API → 프론트엔드
- 에이전트 참조 문서(7~10)를 첫 태스크로 생성
- 사용 시나리오 3개 확정: 프로젝트 시작 흐름, 일일 작업 루틴, 진행 추적
- 요구사항 전체 확정(lock) — 태스크 분해 단계로 진행

## 제약사항

- 의존성 순서: 문서 → DB/모델 → API → 프론트엔드
- 프론트엔드는 백엔드 API 완성 후 시작
- 테스트 반드시 작성



## Stories

### 프로젝트 초기 설정 및 문서화
Git 저장소 초기화, Docker Compose 설정, 에이전트 참조 문서(ARCHITECTURE.md, CONVENTIONS.md, api-spec.md, agents/*.md) 생성
- Sub-tasks: 5개

### 데이터베이스 모델 및 마이그레이션
SQLAlchemy 모델 정의(Epic, Story, Task, Label, TaskLabel), Alembic 마이그레이션, Pydantic 스키마
- Sub-tasks: 5개

### 태스크 관리 API
태스크 CRUD, 상태 전환, 필터/검색 API 엔드포인트 및 테스트
- Sub-tasks: 4개

### 에픽/스토리/라벨 API
에픽 CRUD, 스토리 CRUD, 라벨 CRUD 및 태스크-라벨 연결 API
- Sub-tasks: 5개

### 프론트엔드 기초 및 공통 컴포넌트
Vite+React+TS+Tailwind 초기 설정, 라우팅, API 클라이언트, 공통 UI 컴포넌트
- Sub-tasks: 4개

### 칸반 보드 및 태스크 관리 UI
칸반 보드 뷰(드래그앤드롭), 태스크 생성/수정 모달, 필터/검색 UI
- Sub-tasks: 4개

### 대시보드 및 통합/배포
대시보드 페이지(진행률 차트, 에픽별 완료율, 활동 타임라인), E2E 테스트, Docker 배포, 최종 문서 업데이트
- Sub-tasks: 8개


---
> 이 파일은 Director Agent가 자동 생성합니다. 에이전트가 코드 생성 시 참조합니다.
