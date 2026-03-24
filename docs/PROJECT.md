# Personal Jira 백엔드 API

## 프로젝트 개요
개인용 이슈 트래킹 시스템의 백엔드 REST API. FastAPI/SQLAlchemy(async)/PostgreSQL 기반으로 Issue CRUD, 상태 변경, 필터링, 헬스체크를 제공한다.

## 목적
개인용 이슈 트래킹 시스템 — 이슈의 생성/관리/상태추적을 REST API로 제공

## 대상 사용자
개인 사용자 (1인)

## 범위
MVP

## 기술 스택
- **backend**: Python, FastAPI
- **database**: PostgreSQL, SQLAlchemy (async), Alembic
- **etc**: pytest, httpx

## 설계 결정사항

- 백엔드 전용 REST API로 구현, 인증 레이어 없음
- Issue 상태는 todo/in_progress/done 3가지 enum
- 필터링은 query parameter 기반 (status, priority)
- 테스트는 pytest + httpx AsyncClient로 작성

## 제약사항

- 태스크 10개 이내
- 테스트 필수
- 인증 없음

## Non-Goals

- 프론트엔드
- 인증/인가
- 배포/인프라

## Stories

### 프로젝트 초기 설정
프로젝트 디렉토리 구조, pyproject.toml, FastAPI 앱 엔트리포인트, 설정(config) 모듈을 구성한다.
- Sub-tasks: 1개

### 데이터베이스 계층
SQLAlchemy async 모델/세션 설정, Pydantic 스키마, Alembic 마이그레이션을 구성한다.
- Sub-tasks: 2개

### Issue API
Issue CRUD 엔드포인트, 상태 변경(todo/in_progress/done), query parameter 기반 필터링(status, priority)을 구현한다.
- Sub-tasks: 3개

### 헬스체크
서버 상태 확인용 헬스체크 엔드포인트를 구현한다.
- Sub-tasks: 1개

### 테스트
pytest + httpx AsyncClient 기반으로 전체 API 엔드포인트의 통합 테스트를 작성한다.
- Sub-tasks: 1개


---
> 이 파일은 Director Agent가 자동 생성합니다. 에이전트가 코드 생성 시 참조합니다.
