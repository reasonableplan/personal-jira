# Personal Jira Backend API

## 프로젝트 개요
개인용 이슈 트래킹 시스템의 백엔드 API. FastAPI + SQLAlchemy(async) + PostgreSQL 기반 MVP.

## 목적
개인용 이슈 트래킹 시스템의 백엔드 서버

## 대상 사용자
개인 사용자 (1인)

## 범위
MVP

## 기술 스택
- **backend**: Python, FastAPI, SQLAlchemy (async), Alembic
- **database**: PostgreSQL
- **etc**: pytest, httpx

## 설계 결정사항

- 기술 스택 확정: FastAPI + SQLAlchemy(async) + PostgreSQL + Alembic + pytest/httpx
- 스코프: MVP 수준, 백엔드 API only
- Issue 상태: TODO/IN_PROGRESS/DONE, 전이 제약 없음
- Issue 우선순위: LOW/MEDIUM/HIGH/CRITICAL
- 요구사항 확정 → 태스크 분해 단계로 진행

## 제약사항

- 백엔드 API만 구현
- 인증/인가 없음
- 태스크 10개 이내
- 테스트 필수

## Non-Goals

- 프론트엔드
- 인증/인가 시스템

## Stories

### 프로젝트 초기 설정
프로젝트 디렉토리 구조, 의존성 관리(pyproject.toml), 환경 설정 파일 구성
- Sub-tasks: 1개

### 데이터베이스 계층
SQLAlchemy async 모델 정의, Alembic 마이그레이션 설정, DB 세션 및 앱 설정 관리
- Sub-tasks: 2개

### Issue CRUD API
Issue 생성, 단건/목록 조회, 수정, 삭제 엔드포인트 및 Pydantic 스키마
- Sub-tasks: 2개

### 상태변경 & 필터링 API
Issue 상태 전이 엔드포인트와 상태/우선순위/키워드 기반 필터링 기능
- Sub-tasks: 2개

### 헬스체크 & 테스트
헬스체크 엔드포인트 구현 및 전체 API에 대한 pytest+httpx 테스트
- Sub-tasks: 3개


---
> 이 파일은 Director Agent가 자동 생성합니다. 에이전트가 코드 생성 시 참조합니다.
