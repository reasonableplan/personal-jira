export enum IssueType {
  EPIC = "epic",
  STORY = "story",
  TASK = "task",
  BUG = "bug",
  SUB_TASK = "sub_task",
}

export enum IssueStatus {
  BACKLOG = "backlog",
  READY = "ready",
  IN_PROGRESS = "in_progress",
  IN_REVIEW = "in_review",
  DONE = "done",
  BLOCKED = "blocked",
  ABANDONED = "abandoned",
}

export enum Priority {
  CRITICAL = "critical",
  HIGH = "high",
  MEDIUM = "medium",
  LOW = "low",
}

export const STATUS_LABELS: Record<IssueStatus, string> = {
  [IssueStatus.BACKLOG]: "Backlog",
  [IssueStatus.READY]: "Ready",
  [IssueStatus.IN_PROGRESS]: "In Progress",
  [IssueStatus.IN_REVIEW]: "In Review",
  [IssueStatus.DONE]: "Done",
  [IssueStatus.BLOCKED]: "Blocked",
  [IssueStatus.ABANDONED]: "Abandoned",
};

export const KANBAN_COLUMNS: IssueStatus[] = [
  IssueStatus.BACKLOG,
  IssueStatus.READY,
  IssueStatus.IN_PROGRESS,
  IssueStatus.IN_REVIEW,
  IssueStatus.DONE,
];

export interface Issue {
  id: string;
  title: string;
  description: string;
  issue_type: IssueType;
  status: IssueStatus;
  priority: Priority;
  priority_order: number;
  parent_id: string | null;
  children?: Issue[];
  retry_count: number;
  created_at: string;
  updated_at: string;
}

export interface EpicProgress {
  total: number;
  done: number;
  in_progress: number;
  percentage: number;
}

export interface ReorderRequest {
  issue_id: string;
  new_order: number;
}
