export const ISSUE_STATUS = {
  BACKLOG: 'backlog',
  TODO: 'todo',
  IN_PROGRESS: 'in_progress',
  IN_REVIEW: 'in_review',
  DONE: 'done',
} as const;

export type IssueStatus = (typeof ISSUE_STATUS)[keyof typeof ISSUE_STATUS];

export const ISSUE_PRIORITY = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  URGENT: 'urgent',
} as const;

export type IssuePriority = (typeof ISSUE_PRIORITY)[keyof typeof ISSUE_PRIORITY];

export const STATUS_LABELS: Record<IssueStatus, string> = {
  [ISSUE_STATUS.BACKLOG]: 'Backlog',
  [ISSUE_STATUS.TODO]: 'To Do',
  [ISSUE_STATUS.IN_PROGRESS]: 'In Progress',
  [ISSUE_STATUS.IN_REVIEW]: 'In Review',
  [ISSUE_STATUS.DONE]: 'Done',
};

export const PRIORITY_LABELS: Record<IssuePriority, string> = {
  [ISSUE_PRIORITY.LOW]: 'Low',
  [ISSUE_PRIORITY.MEDIUM]: 'Medium',
  [ISSUE_PRIORITY.HIGH]: 'High',
  [ISSUE_PRIORITY.URGENT]: 'Urgent',
};

export const KANBAN_COLUMNS: IssueStatus[] = [
  ISSUE_STATUS.BACKLOG,
  ISSUE_STATUS.TODO,
  ISSUE_STATUS.IN_PROGRESS,
  ISSUE_STATUS.IN_REVIEW,
  ISSUE_STATUS.DONE,
];

export interface Issue {
  id: string;
  title: string;
  description: string;
  status: IssueStatus;
  priority: IssuePriority;
  assignee: string | null;
  parent_id: string | null;
  created_at: string;
  updated_at: string;
}