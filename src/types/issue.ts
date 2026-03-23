export const ISSUE_STATUS = {
  BACKLOG: 'backlog',
  READY: 'ready',
  IN_PROGRESS: 'in_progress',
  IN_REVIEW: 'in_review',
  DONE: 'done',
  CANCELLED: 'cancelled',
  BLOCKED: 'blocked',
} as const;

export type IssueStatus = (typeof ISSUE_STATUS)[keyof typeof ISSUE_STATUS];

export const ISSUE_PRIORITY = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical',
} as const;

export type IssuePriority = (typeof ISSUE_PRIORITY)[keyof typeof ISSUE_PRIORITY];

export const ISSUE_TYPE = {
  TASK: 'task',
  BUG: 'bug',
  STORY: 'story',
  EPIC: 'epic',
} as const;

export type IssueType = (typeof ISSUE_TYPE)[keyof typeof ISSUE_TYPE];

export interface Issue {
  id: string;
  title: string;
  description: string;
  status: IssueStatus;
  priority: IssuePriority;
  issue_type: IssueType;
  parent_id: string | null;
  created_at: string;
  updated_at: string;
}
