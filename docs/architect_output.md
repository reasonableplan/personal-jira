파일 쓰기 권한이 차단되고 있어 직접 출력합니다. 아래가 완성된 아키텍처 문서입니다 — 이걸 `docs/architect_output.md`에 붙여넣으시면 됩니다.

---

# Architect Output — Personal Jira

> Sections 5, 6, 7, 9, 10 authored by Architect agent.  
> PM change set applied: no auth, agent-only assignees/comments, 3 new tables.

---

## 5. Authentication

**None.** This system is an internal tool for an agent team + human PM on a trusted network.  
No `users` table, no `refresh_tokens`, no JWT, no session middleware.

All API endpoints are open. Rate limiting and network-level access control (VPN/firewall) are handled at the infrastructure layer, outside application scope.

Remove from tech stack: `python-jose`, `passlib`.

---

## 6. DB Schema

### Design Principles

- Every table has a `BIGSERIAL` surrogate PK named `id`.
- All timestamps are `TIMESTAMPTZ NOT NULL DEFAULT NOW()`.
- Foreign keys use `ON DELETE CASCADE` unless data must be preserved for audit.
- Enum-like columns use `TEXT` with a `CHECK` constraint — avoids Alembic enum migration pain.
- No nullable FKs except where genuinely optional (e.g. `sprint_id` on issues).

---

### agents

Registered agent instances. Populated at system boot from `agents.yaml`.

```sql
CREATE TABLE agents (
    id          BIGSERIAL PRIMARY KEY,
    name        TEXT        NOT NULL UNIQUE,
    role        TEXT        NOT NULL
                    CHECK (role IN (
                        'architect', 'designer', 'orchestrator',
                        'backend_coder', 'frontend_coder', 'reviewer', 'qa'
                    )),
    provider    TEXT        NOT NULL DEFAULT 'claude_cli',
    model       TEXT        NOT NULL,
    status      TEXT        NOT NULL DEFAULT 'idle'
                    CHECK (status IN ('idle', 'busy', 'offline')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

### projects

```sql
CREATE TABLE projects (
    id              BIGSERIAL PRIMARY KEY,
    name            TEXT        NOT NULL,
    description     TEXT,
    skeleton_ref    TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

### sprints

```sql
CREATE TABLE sprints (
    id          BIGSERIAL PRIMARY KEY,
    project_id  BIGINT      NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name        TEXT        NOT NULL,
    goal        TEXT,
    status      TEXT        NOT NULL DEFAULT 'PLANNED'
                    CHECK (status IN ('PLANNED', 'ACTIVE', 'COMPLETED')),
    start_date  DATE,
    end_date    DATE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT sprints_dates_check CHECK (
        start_date IS NULL OR end_date IS NULL OR start_date <= end_date
    )
);

CREATE INDEX idx_sprints_project ON sprints(project_id);
```

---

### labels

```sql
CREATE TABLE labels (
    id      BIGSERIAL PRIMARY KEY,
    name    TEXT NOT NULL UNIQUE,
    color   TEXT NOT NULL DEFAULT '#6B7280'
);
```

---

### issues

Core entity. **No human assignee — agent-only.**

```sql
CREATE TABLE issues (
    id                  BIGSERIAL PRIMARY KEY,
    project_id          BIGINT      NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    sprint_id           BIGINT      REFERENCES sprints(id) ON DELETE SET NULL,
    assignee_agent_id   BIGINT      REFERENCES agents(id) ON DELETE SET NULL,

    title               TEXT        NOT NULL,
    description         TEXT,
    status              TEXT        NOT NULL DEFAULT 'TODO'
                            CHECK (status IN ('TODO', 'IN_PROGRESS', 'REVIEW', 'DONE', 'CANCELLED')),
    priority            TEXT        NOT NULL DEFAULT 'MEDIUM'
                            CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),

    skeleton_section    TEXT,       -- e.g. "§7 GET /api/issues"
    pr_url              TEXT,
    pr_number           INT,
    attempt_count       INT         NOT NULL DEFAULT 0,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_issues_project    ON issues(project_id);
CREATE INDEX idx_issues_sprint     ON issues(sprint_id);
CREATE INDEX idx_issues_assignee   ON issues(assignee_agent_id);
CREATE INDEX idx_issues_status     ON issues(status);
```

---

### issue_labels

```sql
CREATE TABLE issue_labels (
    issue_id    BIGINT NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    label_id    BIGINT NOT NULL REFERENCES labels(id) ON DELETE CASCADE,
    PRIMARY KEY (issue_id, label_id)
);
```

---

### issue_dependencies

```sql
CREATE TABLE issue_dependencies (
    blocker_id  BIGINT NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    blocked_id  BIGINT NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    PRIMARY KEY (blocker_id, blocked_id),
    CONSTRAINT no_self_dependency CHECK (blocker_id <> blocked_id)
);

CREATE INDEX idx_deps_blocked ON issue_dependencies(blocked_id);
```

Cycle detection enforced at the application layer before insert.

---

### comments

**Author may be an agent or a human.** `author_agent_id` is nullable (NULL = human author). `author_name` is always present — populated from `agents.name` or the human's display name.

```sql
CREATE TABLE comments (
    id              BIGSERIAL PRIMARY KEY,
    issue_id        BIGINT      NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    author_agent_id BIGINT      REFERENCES agents(id) ON DELETE SET NULL,  -- NULL = human author
    author_name     TEXT        NOT NULL,  -- agent name or human name, always required

    body            TEXT        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT comments_author_name_nonempty CHECK (char_length(author_name) > 0)
);

CREATE INDEX idx_comments_issue ON comments(issue_id);
```

---

### agent_execution_logs

Per-issue per-attempt execution record. One row per agent run.

```sql
CREATE TABLE agent_execution_logs (
    id              BIGSERIAL PRIMARY KEY,
    issue_id        BIGINT      NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    agent_id        BIGINT      NOT NULL REFERENCES agents(id) ON DELETE RESTRICT,
    attempt_number  INT         NOT NULL,
    token_input     INT         NOT NULL DEFAULT 0,
    token_output    INT         NOT NULL DEFAULT 0,
    duration_ms     INT         NOT NULL DEFAULT 0,
    status          TEXT        NOT NULL
                        CHECK (status IN ('success', 'failed', 'timeout')),
    error_message   TEXT,                              -- NULL on success
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT exec_logs_attempt_positive CHECK (attempt_number >= 1),
    CONSTRAINT exec_logs_tokens_nonneg    CHECK (token_input >= 0 AND token_output >= 0),
    CONSTRAINT exec_logs_duration_nonneg  CHECK (duration_ms >= 0)
);

CREATE INDEX idx_exec_logs_issue ON agent_execution_logs(issue_id);
CREATE INDEX idx_exec_logs_agent ON agent_execution_logs(agent_id);
```

---

### reject_history

Immutable audit of every Reviewer → Coder rejection cycle.

```sql
CREATE TABLE reject_history (
    id                  BIGSERIAL PRIMARY KEY,
    issue_id            BIGINT      NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    reviewer_agent_id   BIGINT      NOT NULL REFERENCES agents(id) ON DELETE RESTRICT,
    coder_agent_id      BIGINT      NOT NULL REFERENCES agents(id) ON DELETE RESTRICT,
    reject_reason       TEXT        NOT NULL,
    attempt_number      INT         NOT NULL,          -- matches agent_execution_logs.attempt_number
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT reject_history_attempt_positive CHECK (attempt_number >= 1)
);

CREATE INDEX idx_reject_issue    ON reject_history(issue_id);
CREATE INDEX idx_reject_reviewer ON reject_history(reviewer_agent_id);
CREATE INDEX idx_reject_coder    ON reject_history(coder_agent_id);
```

---

### issue_status_history

Immutable append-only audit trail of every status transition.

```sql
CREATE TABLE issue_status_history (
    id                  BIGSERIAL PRIMARY KEY,
    issue_id            BIGINT      NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    from_status         TEXT        NOT NULL
                            CHECK (from_status IN ('TODO', 'IN_PROGRESS', 'REVIEW', 'DONE', 'CANCELLED')),
    to_status           TEXT        NOT NULL
                            CHECK (to_status IN ('TODO', 'IN_PROGRESS', 'REVIEW', 'DONE', 'CANCELLED')),
    changed_by_agent_id BIGINT      REFERENCES agents(id) ON DELETE SET NULL,  -- NULL = system or human
    trigger             TEXT        NOT NULL
                            CHECK (trigger IN (
                                'branch_created', 'pr_created', 'pr_merged',
                                'manual',          -- all human/PM-initiated transitions, including → CANCELLED
                                'reviewer_reject'
                            )),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT status_history_no_noop CHECK (from_status <> to_status)
);

CREATE INDEX idx_status_hist_issue ON issue_status_history(issue_id);
```

---

## 7. API Endpoints

Base path: `/api/v1` | Content-Type: `application/json` | No Authorization header.

### Agents

| Method | Path | Description |
|--------|------|-------------|
| GET | `/agents` | List all agents (filter: `role`, `status`) |
| GET | `/agents/{agent_id}` | Get agent detail |
| PATCH | `/agents/{agent_id}/status` | Update status (`idle`/`busy`/`offline`) |
| GET | `/agents/{agent_id}/issues` | Issues assigned to agent (filter: `status`) |
| GET | `/agents/{agent_id}/execution-logs` | All execution logs for agent (filter: `status`) |

### Projects

| Method | Path | Description |
|--------|------|-------------|
| GET | `/projects` | List projects |
| POST | `/projects` | Create project |
| GET | `/projects/{project_id}` | Get project detail |
| PATCH | `/projects/{project_id}` | Update project |
| DELETE | `/projects/{project_id}` | Delete project |

### Sprints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/projects/{project_id}/sprints` | List sprints |
| POST | `/projects/{project_id}/sprints` | Create sprint |
| GET | `/sprints/{sprint_id}` | Get sprint detail with issue summary |
| PATCH | `/sprints/{sprint_id}` | Update sprint (name, goal, dates) |
| POST | `/sprints/{sprint_id}/start` | Transition sprint → ACTIVE |
| POST | `/sprints/{sprint_id}/complete` | Transition sprint → COMPLETED |
| POST | `/sprints/{sprint_id}/issues/{issue_id}` | Add issue to sprint |
| DELETE | `/sprints/{sprint_id}/issues/{issue_id}` | Remove issue from sprint |

### Issues

| Method | Path | Description |
|--------|------|-------------|
| GET | `/issues` | List (filter: `project_id`, `sprint_id`, `status`, `assignee_agent_id`, `priority`, `label_id`, `q`) |
| POST | `/issues` | Create issue |
| GET | `/issues/{issue_id}` | Get with labels, dependencies, latest exec log |
| PATCH | `/issues/{issue_id}` | Update fields |
| DELETE | `/issues/{issue_id}` | Delete issue |
| PATCH | `/issues/{issue_id}/status` | Transition status (body: `to_status`, `trigger`, `agent_id`) |
| PATCH | `/issues/{issue_id}/assign` | Assign to agent (body: `agent_id`) |
| PATCH | `/issues/{issue_id}/pr` | Link PR (body: `pr_url`, `pr_number`) |

### Issue Labels

| Method | Path | Description |
|--------|------|-------------|
| POST | `/issues/{issue_id}/labels` | Add label (body: `label_id`) |
| DELETE | `/issues/{issue_id}/labels/{label_id}` | Remove label |

### Issue Dependencies

| Method | Path | Description |
|--------|------|-------------|
| GET | `/issues/{issue_id}/dependencies` | Get blockers + blocked-by lists |
| POST | `/issues/{issue_id}/dependencies` | Add blocker (body: `blocker_id`) |
| DELETE | `/issues/{issue_id}/dependencies/{blocker_id}` | Remove blocker |

### Labels

| Method | Path | Description |
|--------|------|-------------|
| GET | `/labels` | List all labels |
| POST | `/labels` | Create (body: `name`, `color`) |
| PATCH | `/labels/{label_id}` | Update |
| DELETE | `/labels/{label_id}` | Delete |

### Comments

| Method | Path | Description |
|--------|------|-------------|
| GET | `/issues/{issue_id}/comments` | List (chronological) |
| POST | `/issues/{issue_id}/comments` | Add (body: `author_agent_id`, `author_name`, `body`) |
| PATCH | `/comments/{comment_id}` | Edit body |
| DELETE | `/comments/{comment_id}` | Delete |

### Execution Logs

| Method | Path | Description |
|--------|------|-------------|
| GET | `/issues/{issue_id}/execution-logs` | All logs for issue |
| POST | `/issues/{issue_id}/execution-logs` | Create log entry |

### Reject History

| Method | Path | Description |
|--------|------|-------------|
| GET | `/issues/{issue_id}/reject-history` | List records |
| POST | `/issues/{issue_id}/reject-history` | Add record |

### Status History

| Method | Path | Description |
|--------|------|-------------|
| GET | `/issues/{issue_id}/status-history` | Full audit trail |

---

## 7a. Response Rules

- **camelCase keys** — all JSON responses use camelCase (FastAPI `alias_generator=to_camel` via `model_config`).
- **Pagination format** — list endpoints that support pagination return:
  ```json
  { "items": [], "total": 0, "page": 1, "limit": 20 }
  ```
- **Dates** — all timestamps are ISO 8601 with UTC offset: `2026-04-01T09:00:00Z`.

---

## 9. Error Codes

All errors return a flat structure:

```json
{
  "error": "Issue 42 not found.",
  "code": "ERR_ISSUE_NOT_FOUND",
  "details": null
}
```

| HTTP | Code | When |
|------|------|------|
| 404 | `ERR_ISSUE_NOT_FOUND` | Issue ID does not exist |
| 404 | `ERR_AGENT_NOT_FOUND` | Agent ID does not exist |
| 404 | `ERR_PROJECT_NOT_FOUND` | Project ID does not exist |
| 404 | `ERR_SPRINT_NOT_FOUND` | Sprint ID does not exist |
| 404 | `ERR_LABEL_NOT_FOUND` | Label ID does not exist |
| 404 | `ERR_COMMENT_NOT_FOUND` | Comment ID does not exist |
| 409 | `ERR_INVALID_STATUS_TRANSITION` | Status move not in allowed matrix |
| 409 | `ERR_DEPENDENCY_CYCLE` | Adding dependency would create a cycle |
| 409 | `ERR_SPRINT_NOT_ACTIVE` | Sprint is not in ACTIVE state |
| 409 | `ERR_SPRINT_ALREADY_ACTIVE` | Another sprint is already ACTIVE in this project |
| 409 | `ERR_DUPLICATE_DEPENDENCY` | Dependency already exists |
| 422 | `ERR_VALIDATION` | Request body failed Pydantic validation |
| 500 | `ERR_INTERNAL` | Unhandled server error (no `err.message` exposed) |

---

## 10. Issue Status Flow

### Status Values

| Value | Meaning |
|-------|---------|
| `TODO` | Created, waiting to be started |
| `IN_PROGRESS` | Agent working (branch exists) |
| `REVIEW` | PR open, awaiting Reviewer |
| `DONE` | PR merged, work complete |
| `CANCELLED` | Dropped; no further work |

### Allowed Transitions

| From | To | Trigger |
|------|----|---------|
| `TODO` | `IN_PROGRESS` | `branch_created` |
| `TODO` | `CANCELLED` | `manual` |
| `IN_PROGRESS` | `REVIEW` | `pr_created` |
| `IN_PROGRESS` | `TODO` | `manual` |
| `IN_PROGRESS` | `CANCELLED` | `manual` |
| `REVIEW` | `DONE` | `pr_merged` |
| `REVIEW` | `IN_PROGRESS` | `reviewer_reject` |
| `REVIEW` | `CANCELLED` | `manual` |
| `DONE` | *(terminal)* | — |
| `CANCELLED` | `TODO` | `manual` (reopen) |

Any unlisted transition → `ERR_INVALID_STATUS_TRANSITION`.

### Auto-Transition Rules (orchestrator layer)

| Event | Transition | Trigger value |
|-------|-----------|---------------|
| Coder creates Git branch | TODO → IN_PROGRESS | `branch_created` |
| Coder opens PR | IN_PROGRESS → REVIEW | `pr_created` |
| PR merged to main | REVIEW → DONE | `pr_merged` |
| Reviewer rejects PR | REVIEW → IN_PROGRESS | `reviewer_reject` |

Every transition writes one row to `issue_status_history` and updates `issues.updated_at`.

### attempt_count Increment Rule

Incremented by app layer (not a DB trigger) when a row is inserted into `reject_history`:

```sql
UPDATE issues SET attempt_count = attempt_count + 1 WHERE id = :issue_id;
```

---

**테이블 요약 (11개):** `agents`, `projects`, `sprints`, `labels`, `issues`, `issue_labels`, `issue_dependencies`, `comments`, `agent_execution_logs`, `reject_history`, `issue_status_history`

---

변경 내역 요약:

1. **comments** — `author_agent_id` nullable (`ON DELETE SET NULL`), `author_name TEXT NOT NULL` 추가, `comments_author_name_nonempty` CHECK 추가. POST body에도 `author_name` 반영.
2. **에러 포맷** — 중첩 `{ error: { code, message } }` → flat `{ "error": "...", "code": "...", "details": null }`.
3. **7a. Response Rules** — camelCase, 페이지네이션 포맷, ISO 8601 날짜 규칙 섹션 추가.
4. **issue_status_history trigger** — `'manual'` 값에 인라인 주석 추가: `-- all human/PM-initiated transitions, including → CANCELLED`. CHECK 값 자체는 이미 포함되어 있어 정확.
