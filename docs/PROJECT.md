# Personal Jira — 에이전트 오케스트레이션용 프로젝트 관리 시스템

## 프로젝트 개요
GitHub Project Board를 대체할 독립형 이슈 관리 시스템. Epic→Story→Task 3계층 이슈 관리, Kanban 보드, 활동 타임라인, AI 에이전트 연동 API를 제공한다.

## 목적
GitHub Project Board를 대체할 독립형 이슈 관리 시스템. AI 에이전트들이 태스크를 선점하고 상태를 관리할 수 있는 프로젝트 보드.

## 대상 사용자
본인(개발자) + AI 에이전트들

## 범위
MVP — 핵심 기능만 동작하는 최소 버전. 인증 없음.

## 기술 스택
- **frontend**: React, Vite, TypeScript
- **backend**: FastAPI, Python, uv
- **database**: PostgreSQL 16, SQLAlchemy, Alembic
- **infra**: Docker Compose, nginx

## 설계 결정사항

- DB 스키마: epics, stories, tasks, labels, activities, agents 6개 테이블 확정
- Kanban 컬럼: Backlog, Ready, In Progress, Review, Done 5개 확정
- 에이전트 API 엔드포인트 4개 확정 (claim, move, activities, board)
- 스코프: MVP 확정 — 인증 없이 핵심 기능만 구현
- MVP 핵심 기능 6개 확정: 이슈 CRUD, 라벨, Kanban, 타임라인, 에이전트 API, Docker Compose

## 제약사항

- backend/ + frontend/ 디렉토리 구조
- postgres port 5434
- postgres 16-alpine

## Non-Goals

- 인증/인가
- 멀티유저 지원
- 알림 시스템

## Stories

### 프로젝트 인프라 셋업
Git 레포 초기화, Docker Compose 구성, 백엔드/프론트엔드 프로젝트 스켈레톤 생성
- Sub-tasks: 4개

### DB 스키마 & 마이그레이션
SQLAlchemy 모델 정의 (6개 테이블), Alembic 초기 마이그레이션 생성
- Sub-tasks: 3개

### 백엔드 핵심 API
Epic/Story/Task CRUD, 라벨 관리, 보드 조회, 활동 타임라인 API 구현
- Sub-tasks: 6개

### 에이전트 연동 API
에이전트 태스크 선점(claim), 상태 전이(move), 활동 기록, 에이전트 등록/하트비트 엔드포인트
- Sub-tasks: 4개

### 프론트엔드 UI
Kanban 보드 (드래그앤드롭), 이슈 상세/생성 모달, 활동 타임라인, 라벨/필터 UI
- Sub-tasks: 8개

### 통합 & 마무리
프론트엔드-백엔드 연동, Docker 빌드 검증, E2E 테스트
- Sub-tasks: 5개


---
> 이 파일은 Director Agent가 자동 생성합니다. 에이전트가 코드 생성 시 참조합니다.
