# Personal Jira — API Specification (공유 계약)

> 이 문서는 백엔드와 프론트엔드가 공유하는 **단일 진실 소스(Single Source of Truth)** 입니다.
> 모든 API 엔드포인트는 이 스펙대로 구현하세요.

## Base URL
`http://localhost:8000/api`

## 공통
- Content-Type: `application/json`
- 페이지네이션: `?page=1&per_page=20` → `{ items: [...], total: N, page: N, per_page: N }`
- 에러 응답: `{ detail: "에러 메시지" }` + 적절한 HTTP status

---

## 1. Epics

### GET /api/epics
응답: `{ items: Epic[], total: int }`

### POST /api/epics
요청: `{ title: string, description?: string }`
응답: `Epic` (201)

### GET /api/epics/{id}
응답: `Epic & { stories: Story[] }`

### PATCH /api/epics/{id}
요청: `{ title?: string, description?: string, status?: string }`
응답: `Epic`

### DELETE /api/epics/{id}
응답: 204

---

## 2. Stories

### GET /api/epics/{epic_id}/stories
응답: `{ items: Story[], total: int }`

### POST /api/epics/{epic_id}/stories
요청: `{ title: string, description?: string, sort_order?: int }`
응답: `Story` (201)

### GET /api/stories/{id}
응답: `Story & { tasks: Task[] }`

### PATCH /api/stories/{id}
요청: `{ title?: string, description?: string, status?: string, sort_order?: int }`
응답: `Story`

### DELETE /api/stories/{id}
응답: 204

---

## 3. Tasks

### GET /api/tasks
쿼리: `?status=&assigned_agent=&label=&q=&page=&per_page=`
응답: `{ items: Task[], total: int }`

### POST /api/stories/{story_id}/tasks
요청:
```json
{
  "title": "string",
  "description": "string?",
  "assigned_agent": "string?",
  "priority": "low | medium | high | critical",
  "labels": ["string"],
  "dependencies": ["task_id"]
}
```
응답: `Task` (201)

### GET /api/tasks/{id}
응답: `Task & { activities: Activity[] }`

### PATCH /api/tasks/{id}
요청: `{ title?, description?, assigned_agent?, priority?, labels?, status? }`
응답: `Task`

### DELETE /api/tasks/{id}
응답: 204

---

## 4. Board

### GET /api/board
응답:
```json
{
  "columns": [
    { "name": "Backlog", "tasks": [Task, ...] },
    { "name": "Ready", "tasks": [Task, ...] },
    { "name": "In Progress", "tasks": [Task, ...] },
    { "name": "Review", "tasks": [Task, ...] },
    { "name": "Done", "tasks": [Task, ...] }
  ]
}
```

### PATCH /api/tasks/{id}/move
요청: `{ column: "Backlog" | "Ready" | "In Progress" | "Review" | "Done" }`
응답: `Task`

---

## 5. Agent API

### POST /api/tasks/{id}/claim
요청: `{ agent_id: string }`
응답: `Task` (200) | 409 (이미 선점됨)

### GET /api/agents
응답: `Agent[]`

### POST /api/agents
요청: `{ id: string, name: string, domain: string }`
응답: `Agent` (201)

### PATCH /api/agents/{id}/heartbeat
응답: 200

---

## 6. Activities (타임라인)

### GET /api/tasks/{id}/activities
쿼리: `?page=&per_page=`
응답: `{ items: Activity[], total: int }`

### POST /api/tasks/{id}/activities
요청:
```json
{
  "actor": "string",
  "action_type": "status_change | comment | review_feedback | code_change",
  "content": {
    "message": "string",
    "from_status": "string?",
    "to_status": "string?"
  }
}
```
응답: `Activity` (201)

---

## 7. Labels

### GET /api/labels
응답: `Label[]`

### POST /api/labels
요청: `{ name: string, color: string }`
응답: `Label` (201)

### DELETE /api/labels/{id}
응답: 204

---

## 타입 정의

```typescript
// Epic
interface Epic {
  id: string;          // UUID
  title: string;
  description: string | null;
  status: "active" | "completed" | "archived";
  created_at: string;  // ISO 8601
  updated_at: string;
}

// Story
interface Story {
  id: string;
  epic_id: string;
  title: string;
  description: string | null;
  status: "active" | "completed";
  sort_order: number;
  created_at: string;
  updated_at: string;
}

// Task
interface Task {
  id: string;
  story_id: string;
  title: string;
  description: string | null;
  status: "backlog" | "ready" | "in-progress" | "review" | "done" | "failed";
  board_column: "Backlog" | "Ready" | "In Progress" | "Review" | "Done";
  assigned_agent: string | null;
  priority: "low" | "medium" | "high" | "critical";
  labels: string[];
  dependencies: string[];
  retry_count: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

// Activity
interface Activity {
  id: string;
  task_id: string;
  actor: string;
  action_type: "status_change" | "comment" | "review_feedback" | "code_change";
  content: Record<string, unknown>;
  created_at: string;
}

// Label
interface Label {
  id: string;
  name: string;
  color: string;  // hex (#0052CC)
}

// Agent
interface Agent {
  id: string;
  name: string;
  domain: string;
  status: "idle" | "busy" | "offline";
  last_heartbeat: string;
}
```
