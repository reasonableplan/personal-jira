# Personal Jira 백엔드 API

## 프로젝트 개요
개인용 이슈 트래커 백엔드. FastAPI + SQLAlchemy(async) + PostgreSQL 기반으로 Issue CRUD, 상태 관리(todo/in_progress/done), 필터링(status/priority), 헬스체크를 REST API로 제공한다.

## 목적
개인용 이슈 트래커. Issue의 생성/조회/수정/삭제 및 상태 관리를 REST API로 제공

## 대상 사용자
개인 개발자 1인 사용

## 범위
MVP - 백엔드 전용

## 기술 스택
- **backend**: Python, FastAPI, SQLAlchemy (async)
- **database**: PostgreSQL
- **infra**: Alembic
- **etc**: pytest, httpx

## 설계 결정사항

- 백엔드 전용 MVP, 프론트엔드/인증/배포 제외
- Issue 상태는 todo/in_progress/done 3가지
- 필터링은 status, priority 두 필드 기준
- 태스크 10개 이내로 구성

## 제약사항

- 인증 없음
- 태스크 10개 이내
- 테스트 필수

## Non-Goals

- 프론트엔드
- 인증/인가
- 배포/인프라

## Stories

### 프로젝트 초기 설정
Git 초기화, 디렉토리 구조, pyproject.toml, FastAPI 앱 엔트리포인트, 설정 모듈 구성
- Sub-tasks: 1개

### 데이터베이스 계층
SQLAlchemy async 모델, DB 세션 관리, Alembic 마이그레이션, Pydantic 요청/응답 스키마 정의
- Sub-tasks: 2개

### Issue API
Issue CRUD 엔드포인트, 상태 변경 전용 엔드포인트, status/priority 필터링 기능
- Sub-tasks: 3개

### 헬스체크
서버 상태 확인용 헬스체크 엔드포인트
- Sub-tasks: 1개

### 테스트
pytest + httpx 기반 API 테스트. Issue CRUD/상태변경/필터링 테스트, 헬스체크 테스트, 전체 통합 테스트
- Sub-tasks: 3개


---
> 이 파일은 Director Agent가 자동 생성합니다. 에이전트가 코드 생성 시 참조합니다.
