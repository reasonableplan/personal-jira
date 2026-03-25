import { describe, it, expect } from "vitest";
import type {
  Epic,
  Story,
  Task,
  Label,
  Activity,
  Agent,
  PaginatedResponse,
  BoardResponse,
  ApiError,
  TaskStatus,
  BoardColumn,
  Priority,
  ActionType,
  AgentStatus,
  EpicWithStories,
  StoryWithTasks,
  TaskWithActivities,
} from "@/types";

describe("Type definitions", () => {
  it("Epic has correct shape", () => {
    const epic: Epic = {
      id: "uuid",
      title: "Test",
      description: null,
      status: "active",
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    };
    expect(epic.id).toBe("uuid");
    expect(["active", "completed", "archived"]).toContain(epic.status);
  });

  it("Story has correct shape", () => {
    const story: Story = {
      id: "uuid",
      epic_id: "epic-uuid",
      title: "Test",
      description: "desc",
      status: "active",
      sort_order: 0,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    };
    expect(story.epic_id).toBe("epic-uuid");
  });

  it("Task has all required fields", () => {
    const task: Task = {
      id: "uuid",
      story_id: "story-uuid",
      title: "Test",
      description: null,
      status: "backlog",
      board_column: "Backlog",
      assigned_agent: null,
      priority: "medium",
      labels: [],
      dependencies: [],
      retry_count: 0,
      created_at: "2026-01-01T00:00:00Z",
      started_at: null,
      completed_at: null,
    };
    expect(task.retry_count).toBe(0);
  });

  it("Activity has correct shape", () => {
    const activity: Activity = {
      id: "uuid",
      task_id: "task-uuid",
      actor: "agent-1",
      action_type: "comment",
      content: { message: "hello" },
      created_at: "2026-01-01T00:00:00Z",
    };
    expect(activity.action_type).toBe("comment");
  });

  it("Label has correct shape", () => {
    const label: Label = { id: "uuid", name: "bug", color: "#FF0000" };
    expect(label.color).toBe("#FF0000");
  });

  it("Agent has correct shape", () => {
    const agent: Agent = {
      id: "agent-1",
      name: "Backend Agent",
      domain: "backend",
      status: "idle",
      last_heartbeat: "2026-01-01T00:00:00Z",
    };
    expect(agent.status).toBe("idle");
  });

  it("PaginatedResponse wraps items", () => {
    const res: PaginatedResponse<Epic> = {
      items: [],
      total: 0,
      page: 1,
      per_page: 20,
    };
    expect(res.items).toEqual([]);
  });

  it("BoardResponse has columns", () => {
    const board: BoardResponse = {
      columns: [
        { name: "Backlog", tasks: [] },
        { name: "Ready", tasks: [] },
        { name: "In Progress", tasks: [] },
        { name: "Review", tasks: [] },
        { name: "Done", tasks: [] },
      ],
    };
    expect(board.columns).toHaveLength(5);
  });

  it("ApiError has detail", () => {
    const err: ApiError = { detail: "Not found" };
    expect(err.detail).toBe("Not found");
  });

  it("TaskStatus union covers all values", () => {
    const statuses: TaskStatus[] = ["backlog", "ready", "in-progress", "review", "done", "failed"];
    expect(statuses).toHaveLength(6);
  });

  it("BoardColumn union covers all values", () => {
    const cols: BoardColumn[] = ["Backlog", "Ready", "In Progress", "Review", "Done"];
    expect(cols).toHaveLength(5);
  });

  it("Priority union covers all values", () => {
    const priorities: Priority[] = ["low", "medium", "high", "critical"];
    expect(priorities).toHaveLength(4);
  });

  it("ActionType union covers all values", () => {
    const types: ActionType[] = ["status_change", "comment", "review_feedback", "code_change"];
    expect(types).toHaveLength(4);
  });

  it("AgentStatus union covers all values", () => {
    const statuses: AgentStatus[] = ["idle", "busy", "offline"];
    expect(statuses).toHaveLength(3);
  });

  it("EpicWithStories extends Epic", () => {
    const e: EpicWithStories = {
      id: "uuid",
      title: "Test",
      description: null,
      status: "active",
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
      stories: [],
    };
    expect(e.stories).toEqual([]);
  });

  it("StoryWithTasks extends Story", () => {
    const s: StoryWithTasks = {
      id: "uuid",
      epic_id: "epic-uuid",
      title: "Test",
      description: null,
      status: "active",
      sort_order: 0,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
      tasks: [],
    };
    expect(s.tasks).toEqual([]);
  });

  it("TaskWithActivities extends Task", () => {
    const t: TaskWithActivities = {
      id: "uuid",
      story_id: "story-uuid",
      title: "Test",
      description: null,
      status: "backlog",
      board_column: "Backlog",
      assigned_agent: null,
      priority: "medium",
      labels: [],
      dependencies: [],
      retry_count: 0,
      created_at: "2026-01-01T00:00:00Z",
      started_at: null,
      completed_at: null,
      activities: [],
    };
    expect(t.activities).toEqual([]);
  });
});
