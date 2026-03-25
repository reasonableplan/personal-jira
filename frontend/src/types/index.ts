export type EpicStatus = "active" | "completed" | "archived";
export type StoryStatus = "active" | "completed";
export type TaskStatus = "backlog" | "ready" | "in-progress" | "review" | "done" | "failed";
export type BoardColumn = "Backlog" | "Ready" | "In Progress" | "Review" | "Done";
export type Priority = "low" | "medium" | "high" | "critical";
export type ActionType = "status_change" | "comment" | "review_feedback" | "code_change";
export type AgentStatus = "idle" | "busy" | "offline";

export interface Epic {
  id: string;
  title: string;
  description: string | null;
  status: EpicStatus;
  created_at: string;
  updated_at: string;
}

export interface Story {
  id: string;
  epic_id: string;
  title: string;
  description: string | null;
  status: StoryStatus;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  story_id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  board_column: BoardColumn;
  assigned_agent: string | null;
  priority: Priority;
  labels: string[];
  dependencies: string[];
  retry_count: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface Activity {
  id: string;
  task_id: string;
  actor: string;
  action_type: ActionType;
  content: Record<string, unknown>;
  created_at: string;
}

export interface Label {
  id: string;
  name: string;
  color: string;
}

export interface Agent {
  id: string;
  name: string;
  domain: string;
  status: AgentStatus;
  last_heartbeat: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}
