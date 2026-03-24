# Personal Jira 백엔드 API

## 프로젝트 개요
개인용 이슈 트래커 REST API — Issue CRUD, 상태변경(todo/in_progress/done), 필터링(status/priority), 헬스체크를 FastAPI + SQLAlchemy(async) + PostgreSQL로 구현

## 목적
개인용 이슈 트래커 백엔드 — 이슈의 생성/관리/상태추적을 위한 REST API

## 대상 사용자
개인 사용자 (1인)

## 범위
MVP

## 기술 스택
- **backend**: Python, FastAPI, SQLAlchemy (async)
- **database**: PostgreSQL
- **infra**: Alembic
- **etc**: pytest, httpx

## 설계 결정사항

- Issue CRUD, 상태변경(todo/in_progress/done), 필터링(status, priority), 헬스체크 4가지 핵심 기능 구현
- 5개 스토리로 분해: 프로젝트 초기설정, DB 계층, Issue API, 헬스체크, 테스트
- 기술 스택: Python/FastAPI/SQLAlchemy(async)/PostgreSQL/Alembic/pytest+httpx

## 제약사항

- 백엔드만
- 인증 없음
- 태스크 10개 이내
- 테스트 필수

## Non-Goals

- 프론트엔드
- 인증/인가
- 배포

## Stories

### 프로젝트 초기 설정
Git 저장소 초기화, 프로젝트 디렉토리 구조 생성, 의존성 정의(pyproject.toml), FastAPI 앱 엔트리포인트 설정
- Sub-tasks: 1개

### 데이터베이스 계층
SQLAlchemy async 엔진/세션 설정, Issue 모델 정의, Alembic 마이그레이션 구성
- Sub-tasks: 2개

### Issue API
Issue CRUD 엔드포인트, 상태변경 엔드포인트, status/priority 필터링 구현
- Sub-tasks: 2개

### 헬스체크
서버 및 DB 연결 상태를 확인하는 /health 엔드포인트
- Sub-tasks: 1개

### 테스트
pytest + httpx 기반 테스트 인프라 구성 및 전체 API 통합 테스트 작성
- Sub-tasks: 2개


---
> 이 파일은 Director Agent가 자동 생성합니다. 에이전트가 코드 생성 시 참조합니다.
