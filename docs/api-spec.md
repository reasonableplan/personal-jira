# API Specification — Personal Jira MVP

> RESTful API 엔드포인트 전체 스펙. 요청/응답 형식, 상태 코드, 공통 규칙 포함.

---

## 목차

- [공통 규칙](#공통-규칙)
- [Epics](#epics)
- [Stories](#stories)
- [Tasks](#tasks)
- [Labels](#labels)
- [Dashboard](#dashboard)

---

## 공통 규칙

### Base URL

```
http://localhost:8000/api
```

### 페이지네이션

목록 조회 엔드포인트는 `offset` / `limit` 방식 페이지네이션을 지원한다.

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `offset` | integer | `0` | 건너뛸 항목 수 |
| `limit` | integer | `50` | 반환할 최대 항목 수 (최대 100) |

**응답 형식:**

```json
{
  "items": [],
  "total": 0,
  "offset": 0,
  "limit": 50
}
```

### 정렬

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `sort_by` | string | `created_at` | 정렬 기준 필드 |
| `order` | string | `desc` | 정렬 방향 (`asc` \| `desc`) |

### 에러 응답

모든 에러는 `detail` 필드를 포함하는 JSON 응답:

```json
{
  "detail": "에러 메시지"
}
```

| 상태 코드 | 의미 | 예시 |
|-----------|------|------|
| `400` | 잘못된 요청 | 유효하지 않은 status 값 |
| `404` | 리소스 없음 | 존재하지 않는 ID |
| `422` | 유효성 검증 실패 | 필수 필드 누락 (FastAPI 자동) |

**422 응답 형식 (FastAPI 기본):**

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

### 공통 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | UUID (string) | 리소스 고유 식별자 |
| `created_at` | ISO 8601 datetime | 생성 시각 |
| `updated_at` | ISO 8601 datetime | 최종 수정 시각 |

---

## Epics

### `GET /api/epics` — 에픽 목록 조회

**쿼리 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `offset` | integer | N | 페이지네이션 오프셋 (기본 0) |
| `limit` | integer | N | 페이지 크기 (기본 50) |
| `sort_by` | string | N | 정렬 필드 (기본 `created_at`) |
| `order` | string | N | `asc` \| `desc` (기본 `desc`) |

**응답: `200 OK`**

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "사용자 인증 시스템",
      "description": "JWT 기반 로그인/회원가입 구현",
      "status": "active",
      "created_at": "2026-03-20T09:00:00Z",
      "updated_at": "2026-03-20T09:00:00Z"
    }
  ],
  "total": 1,
  "offset": 0,
  "limit": 50
}
```

---

### `POST /api/epics` — 에픽 생성

**요청 바디:**

```json
{
  "title": "사용자 인증 시스템",
  "description": "JWT 기반 로그인/회원가입 구현"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `title` | string | Y | 에픽 제목 |
| `description` | string | N | 에픽 설명 (기본 `null`) |

**응답: `201 Created`**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "사용자 인증 시스템",
  "description": "JWT 기반 로그인/회원가입 구현",
  "status": "planning",
  "created_at": "2026-03-20T09:00:00Z",
  "updated_at": "2026-03-20T09:00:00Z"
}
```

**에러:**

| 상태 코드 | 조건 |
|-----------|------|
| `422` | `title` 누락 |

---

### `GET /api/epics/{id}` — 에픽 단건 조회

**경로 파라미터:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `id` | UUID | 에픽 ID |

**응답: `200 OK`**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "사용자 인증 시스템",
  "description": "JWT 기반 로그인/회원가입 구현",
  "status": "active",
  "created_at": "2026-03-20T09:00:00Z",
  "updated_at": "2026-03-20T09:00:00Z"
}
```

**에러:**

| 상태 코드 | 조건 |
|-----------|------|
| `404` | 해당 ID의 에픽이 없음 |

---

### `PUT /api/epics/{id}` — 에픽 수정

**경로 파라미터:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `id` | UUID | 에픽 ID |

**요청 바디:**

```json
{
  "title": "사용자 인증 시스템 v2",
  "description": "OAuth2 + JWT 기반 인증",
  "status": "active"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `title` | string | N | 에픽 제목 |
| `description` | string | N | 에픽 설명 |
| `status` | string | N | `planning` \| `active` \| `done` |

**응답: `200 OK`**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "사용자 인증 시스템 v2",
  "description": "OAuth2 + JWT 기반 인증",
  "status": "active",
  "created_at": "2026-03-20T09:00:00Z",
  "updated_at": "2026-03-21T10:30:00Z"
}
```

**에러:**

| 상태 코드 | 조건 |
|-----------|------|
| `400` | 유효하지 않은 `status` 값 |
| `404` | 해당 ID의 에픽이 없음 |

---

### `DELETE /api/epics/{id}` — 에픽 삭제

**경로 파라미터:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `id` | UUID | 에픽 ID |

**응답: `200 OK`**

```json
{
  "detail": "Epic deleted"
}
```

**에러:**

| 상태 코드 | 조건 |
|-----------|------|
| `404` | 해당 ID의 에픽이 없음 |

---

## Stories

### `GET /api/epics/{epic_id}/stories` — 에픽 내 스토리 목록 조회

**경로 파라미터:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `epic_id` | UUID | 에픽 ID |

**쿼리 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `offset` | integer | N | 페이지네이션 오프셋 (기본 0) |
| `limit` | integer | N | 페이지 크기 (기본 50) |
| `sort_by` | string | N | 정렬 필드 (기본 `created_at`) |
| `order` | string | N | `asc` \| `desc` (기본 `desc`) |

**응답: `200 OK`**

```json
{
  "items": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440002",
      "epic_id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "로그인 페이지 구현",
      "description": "이메일/비밀번호 로그인 폼",
      "status": "in_progress",
      "priority": 1,
      "created_at": "2026-03-20T10:00:00Z",
      "updated_at": "2026-03-20T10:00:00Z"
    }
  ],
  "total": 1,
  "offset": 0,
  "limit": 50
}
```

**에러:**

| 상태 코드 | 조건 |
|-----------|------|
| `404` | 해당 `epic_id`의 에픽이 없음 |

---

### `POST /api/stories` — 스토리 생성

**요청 바디:**

```json
{
  "epic_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "로그인 페이지 구현",
  "description": "이메일/비밀번호 로그인 폼",
  "priority": 1
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `epic_id` | UUID | Y | 소속 에픽 ID |
| `title` | string | Y | 스토리 제목 |
| `description` | string | N | 스토리 설명 (기본 `null`) |
| `priority` | integer | N | 우선순위 (기본 `0`, 높을수록 우선) |

**응답: `201 Created`**

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440002",
  "epic_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "로그인 페이지 구현",
  "description": "이메일/비밀번호 로그인 폼",
  "status": "todo",
  "priority": 1,
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": "2026-03-20T10:00:00Z"
}
```

**에러:**

| 상태 코드 | 조건 |
|-----------|------|
| `404` | 해당 `epic_id`의 에픽이 없음 |
| `422` | `title` 또는 `epic_id` 누락 |

---

### `GET /api/stories/{id}` — 스토리 단건 조회

**경로 파라미터:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `id` | UUID | 스토리 ID |

**응답: `200 OK`**

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440002",
  "epic_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "로그인 페이지 구현",
  "description": "이메일/비밀번호 로그인 폼",
  "status": "in_progress",
  "priority": 1,
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": "2026-03-20T10:00:00Z"
}
```

**에러:**

| 상태 코드 | 조건 |
|-----------|------|
| `404` | 해당 ID의 스토리가 없음 |

---

### `PUT /api/stories/{id}` — 스토리 수정

**경로 파라미터:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `id` | UUID | 스토리 ID |

**요청 바디:**

```json
{
  "title": "로그인 페이지 구현 (수정)",
  "description": "이메일/비밀번호 + 소셜 로그인",
  "status": "in_progress",
  "priority": 2
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `title` | string | N | 스토리 제목 |
| `description` | string | N | 스토리 설명 |
| `status` | string | N | `todo` \| `in_progress` \| `done` |
| `priority` | integer | N | 우선순위 |

**응답: `200 OK`**

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440002",
  "epic_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "로그인 페이지 구현 (수정)",
  "description": "이메일/비밀번호 + 소셜 로그인",
  "status": "in_progress",
  "priority": 2,
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": "2026-03-21T11:00:00Z"
}
```

**에러:**

| 상태 코드 | 조건 |
|-----------|------|
| `400` | 유효하지 않은 `status` 값 |
| `404` | 해당 ID의 스토리가 없음 |

---

### `DELETE /api/stories/{id}` — 스토리 삭제

**경로 파라미터:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `id` | UUID | 스토리 ID |

**응답: `200 OK`**

```json
{
  "detail": "Story deleted"
}
```

**에러:**

| 상태 코드 | 조건 |
|-----------|------|
| `404` | 해당 ID의 스토리가 없음 |

---

## Tasks

### `GET /api/tasks` — 태스크 목록 조회 (필터/검색)

**쿼리 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `status` | string | N | 상태 필터 (`todo` \| `in_progress` \| `in_review` \| `done`) |
| `priority` | integer | N | 우선순위 필터 |
| `label` | string | N | 라벨명 필터 |
| `search` | string | N | 제목/설명 검색어 |
| `story_id` | UUID | N | 스토리 ID 필터 |
| `offset` | integer | N | 페이지네이션 오프셋 (기본 0) |
| `limit` | integer | N | 페이지 크기 (기본 50) |
| `sort_by` | string | N | 정렬 필드 (기본 `created_at`) |
| `order` | string | N | `asc` \| `desc` (기본 `desc`) |

**응답: `200 OK`**

```json
{
  "items": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440003",
      "story_id": "660e8400-e29b-41d4-a716-446655440002",
      "title": "로그인 API 엔드포인트 구현",
      "description": "POST /api/auth/login 구현",
      "status": "todo",
      "priority": 1,
      "labels": [
        {
          "id": "880e8400-e29b-41d4-a716-446655440004",
          "name": "backend",
          "color": "#3b82f6"
        }
      ],
      "created_at": "2026-03-20T11:00:00Z",
      "updated_at": "2026-03-20T11:00:00Z"
    }
  ],
  "total": 1,
  "offset": 0,
  "limit": 50
}
```

---

### `POST /api/tasks` — 태스크 생성

**요청 바디:**

```json
{
  "story_id": "660e8400-e29b-41d4-a716-446655440002",
  "title": "로그인 API 엔드포인트 구현",
  "description": "POST /api/auth/login 구현",
  "priority": 1
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `story_id` | UUID | Y | 소속 스토리 ID |
| `title` | string | Y | 태스크 제목 |
| `description` | string | N | 태스크 설명 (기본 `null`) |
| `priority` | integer | N | 우선순위 (기본 `0`) |

**응답: `201 Created`**

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "story_id": "660e8400-e29b-41d4-a716-446655440002",
  "title": "로그인 API 엔드포인트 구현",
  "description": "POST /api/auth/login 구현",
  "status": "todo",
  "priority": 1,
  "labels": [],
  "created_at": "2026-03-20T11:00:00Z",
  "updated_at": "2026-03-20T11:00:00Z"
}
```

**에러:**

| 상태 코드 | 조건 |
|-----------|------|
| `404` | 해당 `story_id`의 스토리가 없음 |
| `422` | `title` 또는 `story_id` 누락 |

---

### `GET /api/tasks/{id}` — 태스크 단건 조회

**경로 파라미터:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `id` | UUID | 태스크 ID |

**응답: `200 OK`**

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "story_id": "660e8400-e29b-41d4-a716-446655440002",
  "title": "로그인 API 엔드포인트 구현",
  "description": "POST /api/auth/login 구현",
  "status": "in_progress",
  "priority": 1,
  "labels": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440004",
      "name": "backend",
      "color": "#3b82f6"
    }
  ],
  "created_at": "2026-03-20T11:00:00Z",
  "updated_at": "2026-03-21T14:00:00Z"
}
```

**에러:**

| 상태 코드 | 조건 |
|-----------|------|
| `404` | 해당 ID의 태스크가 없음 |

---

### `PUT /api/tasks/{id}` — 태스크 수정

**경로 파라미터:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `id` | UUID | 태스크 ID |

**요청 바디:**

```json
{
  "title": "로그인 API 구현 (JWT)",
  "description": "JWT access/refresh 토큰 발급",
  "status": "in_progress",
  "priority": 2
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `title` | string | N | 태스크 제목 |
| `description` | string | N | 태스크 설명 |
| `status` | string | N | `todo` \| `in_progress` \| `in_review` \| `done` |
| `priority` | integer | N | 우선순위 |

**응답: `200 OK`**

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "story_id": "660e8400-e29b-41d4-a716-446655440002",
  "title": "로그인 API 구현 (JWT)",
  "description": "JWT access/refresh 토큰 발급",
  "status": "in_progress",
  "priority": 2,
  "labels": [],
  "created_at": "2026-03-20T11:00:00Z",
  "updated_at": "2026-03-22T09:30:00Z"
}
```

**에러:**

| 상태 코드 | 조건 |
|-----------|------|
| `400` | 유효하지 않은 `status` 값 |
| `404` | 해당 ID의 태스크가 없음 |

---

### `DELETE /api/tasks/{id}` — 태스크 삭제

**경로 파라미터:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `id` | UUID | 태스크 ID |

**응답: `200 OK`**

```json
{
  "detail": "Task deleted"
}
```

**에러:**

| 상태 코드 | 조건 |
|-----------|------|
| `404` | 해당 ID의 태스크가 없음 |

---

### `PATCH /api/tasks/{id}/status` — 태스크 상태 변경 (칸반 드래그앤드롭)

**경로 파라미터:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `id` | UUID | 태스크 ID |

**요청 바디:**

```json
{
  "status": "in_review"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `status` | string | Y | `todo` \| `in_progress` \| `in_review` \| `done` |

**응답: `200 OK`**

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "story_id": "660e8400-e29b-41d4-a716-446655440002",
  "title": "로그인 API 엔드포인트 구현",
  "description": "POST /api/auth/login 구현",
  "status": "in_review",
  "priority": 1,
  "labels": [],
  "created_at": "2026-03-20T11:00:00Z",
  "updated_at": "2026-03-22T15:00:00Z"
}
```

**에러:**

| 상태 코드 | 조건 |
|-----------|------|
| `400` | 유효하지 않은 `status` 값 |
| `404` | 해당 ID의 태스크가 없음 |

---

## Labels

### `GET /api/labels` — 라벨 목록 조회

**쿼리 파라미터:**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `offset` | integer | N | 페이지네이션 오프셋 (기본 0) |
| `limit` | integer | N | 페이지 크기 (기본 50) |
| `sort_by` | string | N | 정렬 필드 (기본 `created_at`) |
| `order` | string | N | `asc` \| `desc` (기본 `desc`) |

**응답: `200 OK`**

```json
{
  "items": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440004",
      "name": "backend",
      "color": "#3b82f6",
      "created_at": "2026-03-20T08:00:00Z"
    },
    {
      "id": "880e8400-e29b-41d4-a716-446655440005",
      "name": "frontend",
      "color": "#10b981",
      "created_at": "2026-03-20T08:00:00Z"
    }
  ],
  "total": 2,
  "offset": 0,
  "limit": 50
}
```

---

### `POST /api/labels` — 라벨 생성

**요청 바디:**

```json
{
  "name": "bug",
  "color": "#ef4444"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `name` | string | Y | 라벨 이름 (유니크) |
| `color` | string | Y | HEX 색상 코드 |

**응답: `201 Created`**

```json
{
  "id": "880e8400-e29b-41d4-a716-446655440006",
  "name": "bug",
  "color": "#ef4444",
  "created_at": "2026-03-20T12:00:00Z"
}
```

**에러:**

| 상태 코드 | 조건 |
|-----------|------|
| `400` | 동일한 이름의 라벨이 이미 존재 |
| `422` | `name` 또는 `color` 누락 |

---

### `PUT /api/labels/{id}` — 라벨 수정

**경로 파라미터:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `id` | UUID | 라벨 ID |

**요청 바디:**

```json
{
  "name": "critical-bug",
  "color": "#dc2626"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `name` | string | N | 라벨 이름 |
| `color` | string | N | HEX 색상 코드 |

**응답: `200 OK`**

```json
{
  "id": "880e8400-e29b-41d4-a716-446655440006",
  "name": "critical-bug",
  "color": "#dc2626",
  "created_at": "2026-03-20T12:00:00Z"
}
```

**에러:**

| 상태 코드 | 조건 |
|-----------|------|
| `400` | 동일한 이름의 라벨이 이미 존재 |
| `404` | 해당 ID의 라벨이 없음 |

---

### `DELETE /api/labels/{id}` — 라벨 삭제

**경로 파라미터:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `id` | UUID | 라벨 ID |

**응답: `200 OK`**

```json
{
  "detail": "Label deleted"
}
```

**에러:**

| 상태 코드 | 조건 |
|-----------|------|
| `404` | 해당 ID의 라벨이 없음 |

---

## Dashboard

### `GET /api/dashboard/summary` — 대시보드 요약

프로젝트 전체 진행 현황을 요약한다.

**응답: `200 OK`**

```json
{
  "total_epics": 3,
  "total_stories": 12,
  "total_tasks": 45,
  "tasks_by_status": {
    "todo": 20,
    "in_progress": 15,
    "in_review": 5,
    "done": 5
  },
  "completion_rate": 11.1,
  "epics_summary": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "사용자 인증 시스템",
      "status": "active",
      "total_tasks": 15,
      "completed_tasks": 3,
      "completion_rate": 20.0
    }
  ],
  "recent_activities": [
    {
      "entity_type": "task",
      "entity_id": "770e8400-e29b-41d4-a716-446655440003",
      "entity_title": "로그인 API 엔드포인트 구현",
      "action": "status_changed",
      "detail": "todo → in_progress",
      "timestamp": "2026-03-22T15:00:00Z"
    }
  ]
}
```

**응답 필드 설명:**

| 필드 | 타입 | 설명 |
|------|------|------|
| `total_epics` | integer | 전체 에픽 수 |
| `total_stories` | integer | 전체 스토리 수 |
| `total_tasks` | integer | 전체 태스크 수 |
| `tasks_by_status` | object | 상태별 태스크 수 |
| `completion_rate` | float | 전체 완료율 (%) — `done` 태스크 / 전체 태스크 * 100 |
| `epics_summary` | array | 에픽별 진행 현황 |
| `epics_summary[].completion_rate` | float | 에픽별 완료율 (%) |
| `recent_activities` | array | 최근 활동 내역 (최대 20건) |

---

## 엔드포인트 요약

| # | 메서드 | URL | 설명 |
|---|--------|-----|------|
| 1 | `GET` | `/api/epics` | 에픽 목록 조회 |
| 2 | `POST` | `/api/epics` | 에픽 생성 |
| 3 | `GET` | `/api/epics/{id}` | 에픽 단건 조회 |
| 4 | `PUT` | `/api/epics/{id}` | 에픽 수정 |
| 5 | `DELETE` | `/api/epics/{id}` | 에픽 삭제 |
| 6 | `GET` | `/api/epics/{epic_id}/stories` | 에픽 내 스토리 목록 |
| 7 | `POST` | `/api/stories` | 스토리 생성 |
| 8 | `GET` | `/api/stories/{id}` | 스토리 단건 조회 |
| 9 | `PUT` | `/api/stories/{id}` | 스토리 수정 |
| 10 | `DELETE` | `/api/stories/{id}` | 스토리 삭제 |
| 11 | `GET` | `/api/tasks` | 태스크 목록 (필터/검색) |
| 12 | `POST` | `/api/tasks` | 태스크 생성 |
| 13 | `GET` | `/api/tasks/{id}` | 태스크 단건 조회 |
| 14 | `PUT` | `/api/tasks/{id}` | 태스크 수정 |
| 15 | `DELETE` | `/api/tasks/{id}` | 태스크 삭제 |
| 16 | `PATCH` | `/api/tasks/{id}/status` | 태스크 상태 변경 |
| 17 | `GET` | `/api/labels` | 라벨 목록 조회 |
| 18 | `POST` | `/api/labels` | 라벨 생성 |
| 19 | `PUT` | `/api/labels/{id}` | 라벨 수정 |
| 20 | `DELETE` | `/api/labels/{id}` | 라벨 삭제 |
| 21 | `GET` | `/api/dashboard/summary` | 대시보드 요약 |
