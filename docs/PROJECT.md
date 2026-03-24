# Personal Jira 백엔드 API

## 프로젝트 개요
개인용 이슈 트래커 백엔드 API. FastAPI/SQLAlchemy(async)/PostgreSQL 기반으로 이슈 CRUD, 상태변경, 필터링, 헬스체크를 제공한다.

## 목적
개인용 이슈 트래커 - 이슈의 생성/관리/상태추적을 위한 백엔드 API

## 대상 사용자
개인 사용자 (1인)

## 범위
MVP

## 기술 스택
- **backend**: Python, FastAPI, SQLAlchemy (async), Alembic
- **database**: PostgreSQL
- **etc**: pytest, httpx

## 설계 결정사항

- MVP 범위: 백엔드 API만, 인증 없음
- 기술 스택 확정: FastAPI + SQLAlchemy async + PostgreSQL + Alembic + pytest/httpx
- 핵심 기능 4개: CRUD, 상태변경, 필터링, 헬스체크
- 태스크 10개 이내로 분해

## 제약사항

- 태스크 10개 이내
- 테스트 필수
- 백엔드만

## Non-Goals

- 프론트엔드
- 인증/인가
- 배포

## Stories

### 프로젝트 초기 설정
Git 저장소 초기화, 디렉토리 구조 생성, pyproject.toml 및 의존성 설정
- Sub-tasks: 1개

### 데이터베이스 계층
async SQLAlchemy 엔진/세션 설정, Issue 모델 정의, Alembic 마이그레이션 생성
- Sub-tasks: 2개

### API 엔드포인트
FastAPI 앱 설정, Pydantic 스키마, 헬스체크, 이슈 CRUD, 상태변경, 필터링 API 구현
- Sub-tasks: 4개

### 테스트
pytest + httpx 기반 테스트 환경 구성 및 전체 API 통합 테스트 작성
- Sub-tasks: 2개


---
> 이 파일은 Director Agent가 자동 생성합니다. 에이전트가 코드 생성 시 참조합니다.
