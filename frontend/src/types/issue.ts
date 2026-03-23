export enum IssueStatus {
  BACKLOG = 'backlog',
  TODO = 'todo',
  IN_PROGRESS = 'in_progress',
  IN_REVIEW = 'in_review',
  DONE = 'done',
  CANCELLED = 'cancelled',
}

export enum IssuePriority {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

export enum IssueType {
  EPIC = 'epic',
  STORY = 'story',
  TASK = 'task',
  BUG = 'bug',
  SUBTASK = 'subtask',
}

export interface Issue {
  id: string;
  title: string;
  description?: string;
  issue_type: IssueType;
  status: IssueStatus;
  priority: IssuePriority;
  assignee?: string;
  parent_id?: string;
  labels: string[];
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  status_counts: Record<IssueStatus, number>;
  priority_counts: Record<IssuePriority, number>;
  daily_created: { date: string; count: number }[];
  daily_resolved: { date: string; count: number }[];
}

export type WsEventType = 'issue_created' | 'issue_updated' | 'issue_deleted' | 'issue_status_changed';

export interface WsEvent {
  type: WsEventType;
  payload: Issue;
  timestamp: string;
}
