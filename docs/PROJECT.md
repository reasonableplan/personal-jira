# Personal Jira 백엔드 API

## 프로젝트 개요
개인용 이슈 트래커 백엔드 MVP. FastAPI + SQLAlchemy(async) + PostgreSQL 기반 Issue CRUD, 상태관리, 필터링, 헬스체크 API를 제공한다.

## 목적
개인용 이슈 트래커 백엔드 - Issue 관리 및 상태 추적

## 대상 사용자
개인 사용자 (1인)

## 범위
MVP

## 기술 스택
- **backend**: Python, FastAPI, SQLAlchemy (async), Alembic
- **database**: PostgreSQL
- **etc**: pytest, httpx

## 설계 결정사항

- 백엔드 전용 MVP, 인증 없음
- Issue 모델: status(todo/in_progress/done), priority 필드 포함
- 테스트는 pytest + httpx로 API 레벨 테스트 작성

## 제약사항

- 태스크 10개 이내
- 테스트 필수
- 인증 없음
- 백엔드만

## Non-Goals

- 프론트엔드
- 인증/인가

## Stories

### 프로젝트 초기 설정
Git 저장소, 프로젝트 구조, 의존성, DB 연결 설정 등 인프라 기반 작업
- Sub-tasks: 2개

### 데이터베이스 모델 & 마이그레이션
Issue 모델 정의 및 Alembic 마이그레이션 생성
- Sub-tasks: 1개

### Issue CRUD API
Issue 생성, 조회, 수정, 삭제 엔드포인트 구현
- Sub-tasks: 2개

### 상태 변경 & 필터링 API
Issue 상태 전환 엔드포인트 및 status/priority 기반 필터링 구현
- Sub-tasks: 1개

### 헬스체크 & 테스트
헬스체크 엔드포인트 및 전체 API 테스트 작성
- Sub-tasks: 3개


---
> 이 파일은 Director Agent가 자동 생성합니다. 에이전트가 코드 생성 시 참조합니다.
