# Personal Jira 백엔드 API

## 프로젝트 개요
개인용 이슈 트래커 백엔드 MVP. FastAPI/SQLAlchemy(async)/PostgreSQL 기반 Issue CRUD, 상태관리, 필터링, 헬스체크 REST API와 통합 테스트를 제공한다.

## 목적
개인용 이슈 트래커 - Issue의 생성/관리/상태추적을 위한 REST API

## 대상 사용자
개인 사용자 (1인)

## 범위
MVP - 백엔드 전용

## 기술 스택
- **backend**: Python, FastAPI, SQLAlchemy (async)
- **database**: PostgreSQL
- **infra**: Alembic
- **etc**: pytest, httpx

## 설계 결정사항

- 백엔드 전용 MVP로 확정 - 프론트엔드/인증 제외
- Python/FastAPI/SQLAlchemy(async)/PostgreSQL/Alembic/pytest+httpx 스택 확정
- 핵심 기능: Issue CRUD, 상태변경, 필터링, 헬스체크
- 태스크 10개 이내 제약 확정

## 제약사항

- 태스크 10개 이내
- 테스트 필수
- 인증 없음
- 백엔드만

## Non-Goals

- 프론트엔드
- 인증/인가
- 배포/CI/CD

## Stories

### 프로젝트 인프라 설정
프로젝트 디렉토리 구조, 의존성 관리(pyproject.toml), FastAPI 앱 진입점, 설정 모듈을 구성한다.
- Sub-tasks: 1개

### 데이터베이스 계층
SQLAlchemy async 모델, Alembic 마이그레이션, Pydantic 요청/응답 스키마를 정의한다.
- Sub-tasks: 2개

### Issue API
Issue의 생성/조회/수정/삭제 CRUD와 상태 변경(todo→in_progress→done), status·priority 필터링 엔드포인트를 구현한다.
- Sub-tasks: 2개

### 헬스체크
서버 상태 확인용 /health 엔드포인트를 제공한다.
- Sub-tasks: 1개

### 테스트
pytest+httpx 기반 테스트 환경을 구성하고 전체 API에 대한 통합 테스트를 작성한다.
- Sub-tasks: 2개


---
> 이 파일은 Director Agent가 자동 생성합니다. 에이전트가 코드 생성 시 참조합니다.
