# Personal Jira 백엔드 API

## 프로젝트 개요
개인용 이슈 트래커 백엔드 API. Issue CRUD, 상태변경(todo/in_progress/done), 필터링, 헬스체크를 FastAPI + SQLAlchemy(async) + PostgreSQL로 구현한다.

## 목적
개인용 이슈 트래커 - 이슈의 생성/관리/상태추적을 위한 REST API

## 대상 사용자
개인 사용자 (1인)

## 범위
MVP - 백엔드 API only

## 기술 스택
- **backend**: Python, FastAPI
- **database**: PostgreSQL, SQLAlchemy (async), Alembic
- **etc**: pytest, httpx

## 설계 결정사항

- 백엔드 API만 구현 (프론트엔드 없음)
- 인증/인가 없이 오픈 API로 구현
- Issue 상태는 todo/in_progress/done 3단계
- 테스트는 pytest + httpx로 필수 작성

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
FastAPI 애플리케이션 구조, 설정 관리, 의존성 정의, DB 연결 설정을 포함한 프로젝트 스캐폴딩
- Sub-tasks: 1개

### 데이터베이스 설계 및 스키마
SQLAlchemy 비동기 모델 정의, Alembic 마이그레이션 설정, Pydantic 요청/응답 스키마 정의
- Sub-tasks: 2개

### Issue API
Issue CRUD 엔드포인트, 상태변경 전용 엔드포인트, status/priority 기반 필터링 구현
- Sub-tasks: 3개

### 헬스체크
서버 상태 확인용 /health 엔드포인트
- Sub-tasks: 1개

### 테스트
pytest + httpx 기반 테스트 인프라 구축 및 전체 API 통합 테스트 작성
- Sub-tasks: 2개


---
> 이 파일은 Director Agent가 자동 생성합니다. 에이전트가 코드 생성 시 참조합니다.
