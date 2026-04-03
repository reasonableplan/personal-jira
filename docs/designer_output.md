파일 저장 권한을 허용해주시면 저장됩니다. 그 전에 완성된 문서를 아래에 출력합니다.

---

# Designer Output — Personal Jira

> Based on `skeleton.md` (requirements) and `architect_output.md` (DB schema + API + status flow).

---

## 1. Screen List

All routes live under a single React SPA. No authentication screens.

| # | Route | Page Name | Key Components |
|---|-------|-----------|----------------|
| 1 | `/` | Redirect | → `/projects` |
| 2 | `/projects` | Project List | `ProjectCard`, `CreateProjectDialog` |
| 3 | `/projects/:projectId` | Project Home | Redirect → board |
| 4 | `/projects/:projectId/board` | Kanban Board | `SprintSelector`, `KanbanBoard`, `IssueCard`, `BoardFilterBar` |
| 5 | `/projects/:projectId/backlog` | Backlog | `BacklogTable`, `IssueRow`, `SprintAssignPopover` |
| 6 | `/projects/:projectId/sprints` | Sprint List | `SprintCard`, `CreateSprintDialog` |
| 7 | `/issues/:issueId` | Issue Detail | `IssueHeader`, `IssueMetaSidebar`, `CommentThread`, `CommentInput`, `ExecutionLogAccordion`, `RejectHistoryTimeline`, `DependencyList`, `StatusHistoryTimeline` |
| 8 | `/agents` | Agent Dashboard | `AgentGrid`, `AgentStatusBadge`, `AgentIssueList` |
| 9 | `/agents/:agentId` | Agent Detail | `AgentProfile`, `AgentStatsBar`, `AgentTaskTabs`, `ExecutionLogTable` |
| 10 | `/labels` | Label Management | `LabelTable`, `LabelColorPicker`, `CreateLabelDialog` |

**Modal overlays (not separate routes):** `CreateIssueDialog`, `EditIssueDialog`, `AssignAgentPopover`, `CreateSprintDialog`, `AddDependencyDialog`

---

## 2. User Flow

### PM Workflow
```
[Project List] → select project
  └─ [Kanban Board]
       ├─ Create Sprint → start sprint
       ├─ Create Issue → assign to agent
       ├─ Drag card (manual status override)
       └─ Click card → [Issue Detail]
            ├─ Execution logs (attempts, tokens)
            ├─ Reject history (reviewer reasons)
            ├─ Status history (full audit)
            ├─ Dependencies (add/remove blockers)
            └─ Write comment (author_name required, author_agent_id = null)
  └─ [Agent Dashboard] → monitor agent load
       └─ [Agent Detail] → per-agent tasks + stats + logs
```

### Agent Workflow (API-driven, reflected live in UI)
```
Orchestrator  → POST /issues, PATCH /issues/:id/assign
Coder         → PATCH status (branch_created → IN_PROGRESS)
              → PATCH /issues/:id/pr → PATCH status (pr_created → REVIEW)
Reviewer      → PATCH status (pr_merged → DONE)
              OR POST /reject-history + PATCH status (reviewer_reject → IN_PROGRESS)
QA            → POST /execution-logs
All agents    → PATCH /agents/:id/status (idle ↔ busy)
```

### Real-time Update Flow
```
WebSocket /ws
  ├─ issue_updated  → invalidate ['issues', id]
  ├─ issue_created  → invalidate ['issues'] list
  ├─ agent_status   → invalidate ['agents', id]
  └─ comment_added  → invalidate ['comments', issueId]
```

---

## 3. Component Tree

```
App
├── AppShell
│   ├── Sidebar
│   │   ├── ProjectSelector (shadcn Select)
│   │   ├── NavItem "Board" | "Backlog" | "Sprints" | "Agents"
│   │   └── BottomNav → NavItem "Labels"
│   └── MainContent  <Outlet />
│
├── pages/ProjectListPage
│   └── ProjectGrid → ProjectCard[] → CreateProjectDialog
│
├── pages/KanbanBoardPage
│   ├── BoardTopBar
│   │   ├── SprintSelector
│   │   ├── BoardFilterBar (assignee, priority, label)
│   │   └── Button "Create Issue"
│   └── KanbanBoard
│       └── KanbanColumn[4]  TODO / IN_PROGRESS / REVIEW / DONE
│           └── IssueCard[]
│               ├── PriorityBadge + LabelChips + AttemptBadge
│               ├── IssueTitle (2-line clamp)
│               ├── SkeletonSectionText (mono)
│               └── PRLink + AgentAvatar
│
├── pages/BacklogPage
│   ├── BacklogFilterBar
│   └── BacklogTable → IssueRow[] (title, status, priority, agent, sprint assign)
│
├── pages/SprintListPage
│   └── SprintCard[] (header, progress bar, Start/Complete actions)
│
├── pages/IssueDetailPage
│   ├── IssueHeader (title inline-edit, StatusBadge, BreadcrumbNav)
│   └── IssueBody  [2-col on ≥md]
│       ├── LeftColumn
│       │   ├── DescriptionEditor
│       │   ├── DependencySection (BlockerList + BlockedByList + AddDialog)
│       │   │   └── [inline error if ERR_DEPENDENCY_CYCLE]
│       │   ├── CommentThread → CommentItem[]
│       │   ├── CommentInput                        ← NEW: PM comment box
│       │   │   ├── Textarea (body, required)
│       │   │   ├── Input (author_name, required)   ← human display name
│       │   │   └── Button "Add Comment"
│       │   └── Tabs
│       │       ├── ExecutionLogAccordion (per-attempt: tokens, duration, status)
│       │       ├── RejectHistoryTimeline (reviewer, reason, attempt#)
│       │       └── StatusHistoryTimeline (from→to, trigger, agent, time)
│       └── RightColumn (IssueMetaSidebar)
│           ├── AssigneeField → AssignAgentPopover
│           ├── PrioritySelect
│           ├── LabelField (multi-select chips)
│           ├── SprintField
│           ├── SkeletonSectionField (mono text)
│           ├── PRLinkField (external link)
│           ├── AttemptCountBadge
│           └── TimestampsBlock
│
├── pages/AgentDashboardPage
│   ├── AgentStatusSummary (idle/busy/offline counts)
│   └── AgentGrid → AgentCard[]
│       ├── AgentAvatar (role icon + ring color)
│       ├── AgentName + role badge + StatusDot
│       ├── CurrentTaskPreview
│       ├── StatsRow                                ← UPDATED
│       │   ├── RejectCount  (e.g. "3 rejected")
│       │   ├── AvgDuration  (e.g. "avg 42s")
│       │   └── SuccessRate  (e.g. "87% success")
│       └── Link → /agents/:agentId (execution logs)
│
├── pages/AgentDetailPage
│   ├── AgentProfile (name, role, model, provider, status)
│   ├── AgentStatsBar                               ← NEW
│   │   ├── TotalTasks
│   │   ├── RejectCount
│   │   ├── AvgDurationMs
│   │   └── SuccessRate (%)
│   ├── AgentTaskTabs                               ← UPDATED tabs
│   │   ├── Tab "My Tasks"    → active issues (IN_PROGRESS + REVIEW)
│   │   ├── Tab "Completed"   → DONE issues
│   │   └── Tab "Rejected"    → issues with reject_history entries
│   └── ExecutionLogTable (paginated, link per row to issue detail)
│
├── pages/LabelManagementPage
│   └── LabelTable → LabelRow[] (color swatch, name, edit, delete)
│
└── shared/
    ├── IssueCard, StatusBadge, PriorityBadge
    ├── AgentAvatar, LabelChip
    ├── EmptyState, ErrorBoundary, LoadingSkeleton
    ├── NotFoundPage                                ← ERR_ISSUE_NOT_FOUND → renders here
```

---

## 4. State Management

### Zustand — Global UI State (`useAppStore`)
```ts
interface AppStore {
  selectedProjectId: number | null;
  setSelectedProjectId: (id: number) => void;

  boardFilters: {
    assigneeAgentIds: number[];
    priorities: IssuePriority[];
    labelIds: number[];
  };
  setBoardFilters: (filters: Partial<BoardFilters>) => void;
  resetBoardFilters: () => void;

  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
}
```
**Rule:** Zustand holds only UI context. Never duplicates server data.

### TanStack Query — Server State
```ts
export const QK = {
  projects:        () => ['projects'],
  project:         (id: number) => ['projects', id],
  sprints:         (projectId: number) => ['projects', projectId, 'sprints'],
  sprint:          (id: number) => ['sprints', id],
  issues:          (filters: IssueFilters) => ['issues', filters],
  issue:           (id: number) => ['issues', id],
  issueComments:   (id: number) => ['issues', id, 'comments'],
  issueExecLogs:   (id: number) => ['issues', id, 'execution-logs'],
  issueRejectHist: (id: number) => ['issues', id, 'reject-history'],
  issueStatusHist: (id: number) => ['issues', id, 'status-history'],
  issueDeps:       (id: number) => ['issues', id, 'dependencies'],
  agents:          () => ['agents'],
  agent:           (id: number) => ['agents', id],
  agentIssues:     (id: number, status?: string) => ['agents', id, 'issues', status],
  agentExecLogs:   (id: number) => ['agents', id, 'execution-logs'],
  labels:          () => ['labels'],
} as const;
```

**Stale time:**
| Data | staleTime |
|------|-----------|
| Issue detail | 10s |
| Issue list / board | 15s |
| Agents | 5s |
| Labels | 5min |
| Projects / Sprints | 1min |

WS events → `queryClient.invalidateQueries(QK.xxx)`. No manual cache writes.

### useState — Local Component State
| Component | State | Type |
|-----------|-------|------|
| `CreateIssueDialog` | `open`, form fields | `boolean`, controlled |
| `CreateSprintDialog` | `open`, form fields | `boolean`, controlled |
| `AssignAgentPopover` | `open` | `boolean` |
| `AddDependencyDialog` | `open`, `searchQuery`, `cycleError` | `boolean`, `string`, `string \| null` |
| `DescriptionEditor` | `editing`, `draft` | `boolean`, `string` |
| `CommentInput` | `body`, `authorName`, `submitting` | `string`, `string`, `boolean` |
| `KanbanBoard` | `draggingIssueId` | `number \| null` |
| `BacklogTable` | `sortKey`, `sortDir` | `string`, `'asc' \| 'desc'` |
| `ExecutionLogAccordion` | `expandedAttempt` | `number \| null` |
| `AgentDetailPage` | `activeTab` | `'my-tasks' \| 'completed' \| 'rejected'` |

---

## 5. Design Guide

### Color Palette
```
Background
  bg-base:           #0F1117   (main app bg)
  bg-surface:        #1A1D27   (card, sidebar, dialog)
  bg-elevated:       #242736   (hover, popover)
  bg-border:         #2E3147   (dividers)

Text
  text-primary:      #F1F3FA
  text-secondary:    #9CA3C4
  text-muted:        #5B6082

Accent
  accent-blue:       #4F76F6   (CTA, links, selected nav)
  accent-blue-hover: #6B8FF8

Issue Status
  TODO:              #5B6082
  IN_PROGRESS:       #4F76F6
  REVIEW:            #F59E0B
  DONE:              #22C55E
  CANCELLED:         #EF4444

Priority
  LOW:               #6B7280
  MEDIUM:            #F59E0B
  HIGH:              #F97316
  CRITICAL:          #EF4444

Agent Status
  idle:              #22C55E
  busy:              #F59E0B
  offline:           #4B5563
```

Defined as CSS custom properties in `src/styles/tokens.css`, mapped in `tailwind.config.ts`.

### Typography
| Token | Size | Weight | Use |
|-------|------|--------|-----|
| `text-display` | 24px | 700 | Page titles |
| `text-heading` | 18px | 600 | Section headings, issue title |
| `text-subheading` | 14px | 600 | Card headers, table headers |
| `text-body` | 14px | 400 | Default prose |
| `text-small` | 12px | 400 | Labels, timestamps |
| `text-mono` | 12px | 400 | Skeleton refs, token counts (JetBrains Mono) |

### Layout
- **App shell:** Fixed sidebar (240px / collapsed 56px) + scrollable main (padding 24px, max-w 1440px)
- **Kanban:** 4 columns, `min-w-[280px]` each, board container `overflow-x: auto`
- **Issue detail:** `flex-1` left col + `w-[280px]` right sidebar, stacked on `< md`

### Responsive Breakpoints

#### Breakpoint Reference
| Breakpoint | px | Tailwind prefix |
|------------|-----|-----------------|
| Mobile | < 768 | *(default)* |
| Tablet | 768–1279 | `md` |
| Desktop | 1280+ | `xl` |

#### Desktop (1280px+)
- Sidebar always visible at 240px (collapsible to 56px icon-rail via toggle button)
- Kanban board: 4 columns side-by-side, horizontal scroll if overflow
- Issue detail: 2-column layout (`flex-1` content + `w-[280px]` meta sidebar)
- Agent dashboard: 3-column `AgentGrid`

#### Tablet (768–1279px)
- Sidebar collapses to icon-rail (56px) by default; expand via toggle button
- Kanban board: horizontal scroll (`overflow-x: auto`), columns `min-w-[260px]`
- Issue detail: single column — meta sidebar stacks below content
- Agent dashboard: 2-column `AgentGrid`
- Dialogs: full-width (`w-full max-w-none mx-4`)

#### Mobile (< 768px)
- Sidebar hidden; **bottom navigation bar** replaces it (`position: fixed; bottom: 0`)
  - Bottom nav items: Board, Backlog, Agents, Labels
- Kanban board: **swipe view** — one status column visible at a time, swipe left/right to switch; column indicator dots at top
- Issue detail: single-column full-width; meta sidebar rendered as collapsible accordion below description
- Cards: full-width (`w-full`), no multi-column grid
- Agent dashboard: single-column list
- Dialogs: bottom sheet (`Sheet` with `side="bottom"`)

### shadcn/ui Component Mapping
| Feature | Component |
|---------|-----------|
| Dialogs | `Dialog` |
| Mobile sidebar | `Sheet` |
| Mobile dialogs | `Sheet` (side="bottom") |
| Dropdowns / popovers | `Popover`, `DropdownMenu` |
| Selects | `Select` |
| Tabs (issue detail, agent detail) | `Tabs` |
| Sprint progress | `Progress` |
| Status/priority badges | `Badge` (with color overrides) |
| Execution log rows | `Accordion` |
| Errors | `Alert` |
| Mutation feedback | `Sonner` (toast) |
| Backlog / logs tables | `Table` |
| Forms | React Hook Form + shadcn `Form` |
| Agent avatar hint | `Tooltip` |
| Inline field errors | `FormMessage` (React Hook Form) |

### CSS Modules Usage
Only for layout rules that can't be expressed in Tailwind:
- `KanbanBoard.module.css` — column `height: calc(100vh - 144px)`
- `IssueCard.module.css` — drag handle cursor + transition
- `AgentAvatar.module.css` — role-color border ring

### Agent Role Icons (Lucide)
| Role | Icon | Ring Color |
|------|------|------------|
| architect | `Building2` | #8B5CF6 |
| designer | `Palette` | #EC4899 |
| orchestrator | `Network` | #4F76F6 |
| backend_coder | `Server` | #F97316 |
| frontend_coder | `Monitor` | #06B6D4 |
| reviewer | `CheckSquare` | #22C55E |
| qa | `TestTube2` | #F59E0B |

### Issue Card Anatomy
```
┌────────────────────────────────────────┐
│ [CRITICAL] [frontend]  [attempt: 3]    │
│                                        │
│ Implement auth callback handler        │
│                                        │
│ §7 POST /api/auth/callback             │
│                                        │
│ [PR #42 ↗]          [◉ frontend_coder] │
└────────────────────────────────────────┘
```
Card bg: `bg-surface`. Border-left 3px solid (status color). Hover: `bg-elevated`.

---

## 6. Error UI Mapping

Maps architect-defined error codes (`architect_output.md` §9) to concrete UI behaviors.

### ERR_ISSUE_NOT_FOUND (HTTP 404)

Rendered when navigating to `/issues/:issueId` and the server returns 404.

- **Component:** `NotFoundPage` (full-page)
- **Content:** "Issue not found" heading, short message, "Back to Board" button
- **Implementation:** In `IssueDetailPage`, if the TanStack Query fetch errors with `status === 404`, render `<NotFoundPage />` in place of the page content. Same pattern for `ERR_PROJECT_NOT_FOUND`, `ERR_SPRINT_NOT_FOUND`.

```
┌─────────────────────────────────┐
│                                 │
│   Issue not found               │
│   This issue may have been      │
│   deleted or the link is wrong. │
│                                 │
│   [← Back to Board]             │
│                                 │
└─────────────────────────────────┘
```

### ERR_INVALID_STATUS_TRANSITION (HTTP 409)

Triggered when a drag-and-drop or manual status change violates the allowed transition matrix.

- **Component:** `Sonner` toast — destructive variant
- **Content:** `"Cannot move to [TO_STATUS]: not a valid transition from [FROM_STATUS]."`
- **Behavior:** Toast auto-dismisses after 4s. The card snaps back to its original column — optimistic update rolled back via TanStack Query `onError` → `queryClient.invalidateQueries`.

```
┌──────────────────────────────────────────┐
│  ⚠ Invalid status transition             │
│  Cannot move to DONE from TODO.          │
└──────────────────────────────────────────┘
```

### ERR_DEPENDENCY_CYCLE (HTTP 409)

Triggered when adding a dependency would create a circular reference.

- **Component:** Inline `Alert` inside `AddDependencyDialog`
- **Content:** `"Adding this dependency creates a cycle."`
- **Behavior:** Dialog stays open, search input retains its value. User must pick a different issue. State: `cycleError: string | null` on `AddDependencyDialog` — set on 409, cleared on input change.

```
┌──────────────────────────────────────────────┐
│ Add Dependency                               │
│                                              │
│ Search issue...  [🔍]                        │
│                                              │
│ ╔══════════════════════════════════════════╗ │
│ ║ ⚠ Adding this dependency creates a cycle║ │
│ ╚══════════════════════════════════════════╝ │
│                                              │
│                          [Cancel]  [Add]     │
└──────────────────────────────────────────────┘
```

### ERR_VALIDATION (HTTP 422)

Triggered when a form submission fails Pydantic validation server-side.

- **Component:** React Hook Form `FormMessage` — per-field inline error
- **Content:** Server returns `details` with field-level messages; mapped to `setError(fieldName, { message })` in the form's `onError` handler.
- **Behavior:** Affected field borders turn red, error message appears below the field. If server returns no `details`, fall back to a `Sonner` toast with the top-level `error` string.

```
┌──────────────────────────────────┐
│ Create Issue                     │
│                                  │
│ Title *                          │
│ ┌──────────────────────────────┐ │
│ │                              │ │
│ └──────────────────────────────┘ │
│ ✕ Title must not be empty.       │  ← FormMessage (red)
│                                  │
│                    [Cancel] [Save]│
└──────────────────────────────────┘
```

---

변경사항 요약 (4개 수정):

1. **Comments** — `CommentInput` 컴포넌트 추가 (Section 1, 3, 4). `author_name` 필드(human display name), `author_agent_id = null`로 POST. `submitting` state로 중복 제출 방지.

2. **Agent Dashboard** — `AgentCard` StatsRow에 `RejectCount`, `AvgDuration`, `SuccessRate` 추가. `AgentDetailPage` 탭을 "In Progress | Review | Done | Rejected" → **"My Tasks | Completed | Rejected"**로 변경. `AgentStatsBar` 컴포넌트 추가. 실행 로그 링크 추가.

3. **Responsive Specs** — Desktop(1280px+) / Tablet(768–1279px) / Mobile(<768px) 3단계로 구체화. Mobile: bottom nav + swipe kanban + bottom sheet dialogs.

4. **Error UI** — Section 6 신규 추가. 4개 에러 코드 → 각각 NotFoundPage / Sonner toast / inline Alert / FormMessage로 매핑.
