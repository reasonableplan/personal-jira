export enum IssueStatus {
  BACKLOG = 'backlog',
  READY = 'ready',
  IN_PROGRESS = 'in_progress',
  IN_REVIEW = 'in_review',
  DONE = 'done',
  CANCELLED = 'cancelled',
  BLOCKED = 'blocked',
}

export enum IssuePriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export interface Issue {
  id: string;
  title: string;
  description: string;
  status: IssueStatus;
  priority: IssuePriority;
  assignee: string | null;
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: string;
  issue_id: string;
  content: string;
  author: string;
  created_at: string;
}

export interface CreateIssueRequest {
  title: string;
  description?: string;
  priority?: IssuePriority;
  assignee?: string;
}

export interface CreateCommentRequest {
  content: string;
}

export const KANBAN_COLUMNS: { status: IssueStatus; label: string }[] = [
  { status: IssueStatus.BACKLOG, label: 'Backlog' },
  { status: IssueStatus.READY, label: 'Ready' },
  { status: IssueStatus.IN_PROGRESS, label: 'In Progress' },
  { status: IssueStatus.IN_REVIEW, label: 'In Review' },
  { status: IssueStatus.DONE, label: 'Done' },
];

export const STATUS_LABELS: Record<IssueStatus, string> = {
  [IssueStatus.BACKLOG]: 'Backlog',
  [IssueStatus.READY]: 'Ready',
  [IssueStatus.IN_PROGRESS]: 'In Progress',
  [IssueStatus.IN_REVIEW]: 'In Review',
  [IssueStatus.DONE]: 'Done',
  [IssueStatus.CANCELLED]: 'Cancelled',
  [IssueStatus.BLOCKED]: 'Blocked',
};
