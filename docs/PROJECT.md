# Personal Jira 백엔드 API

## 프로젝트 개요
개인용 이슈 트래커 REST API. Issue CRUD, 상태 관리(todo/in_progress/done), 필터링(status/priority), 헬스체크를 FastAPI + SQLAlchemy(async) + PostgreSQL로 구현한다.

## 목적
개인용 이슈 트래커 - Issue의 생성/관리/상태추적을 위한 REST API

## 대상 사용자
개인 사용자 (1인)

## 범위
MVP - 백엔드 API만

## 기술 스택
- **backend**: Python, FastAPI, SQLAlchemy (async)
- **database**: PostgreSQL
- **infra**: Alembic
- **etc**: pytest, httpx

## 설계 결정사항

- 백엔드 API만 구현 (프론트엔드 제외)
- 인증/인가 없이 MVP로 진행
- 태스크 10개 이내로 분해
- 모든 기능에 테스트 필수

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
Git 저장소 초기화, 프로젝트 디렉터리 구조 생성, 의존성 설정(pyproject.toml), FastAPI 앱 엔트리포인트 구성
- Sub-tasks: 1개

### 데이터베이스 설정
SQLAlchemy async 엔진/세션 설정, Issue 모델 정의, Alembic 마이그레이션 초기 구성
- Sub-tasks: 2개

### Issue CRUD API
Issue 생성/단건조회/목록조회/수정/삭제 REST 엔드포인트 및 Pydantic 스키마, 테스트
- Sub-tasks: 2개

### 상태 변경 & 필터링
Issue 상태 전이(todo→in_progress→done) 전용 엔드포인트, status/priority 기반 목록 필터링, 테스트
- Sub-tasks: 3개

### 헬스체크 & 통합 테스트
서버 헬스체크 엔드포인트, 전체 시나리오 통합 테스트
- Sub-tasks: 2개


---
> 이 파일은 Director Agent가 자동 생성합니다. 에이전트가 코드 생성 시 참조합니다.
