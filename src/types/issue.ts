export enum IssueType {
  EPIC = 'epic',
  STORY = 'story',
  TASK = 'task',
  BUG = 'bug',
  SUBTASK = 'subtask',
}

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

export interface Issue {
  id: string;
  title: string;
  description: string | null;
  issue_type: IssueType;
  status: IssueStatus;
  priority: IssuePriority;
  assignee: string | null;
  labels: string[];
  required_skills: string[];
  parent_id: string | null;
  context_bundle: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface IssueFilters {
  status?: IssueStatus;
  priority?: IssuePriority;
  issue_type?: IssueType;
  assignee?: string;
  search?: string;
}
