export const ISSUE_STATUSES = [
  'Backlog',
  'Ready',
  'InProgress',
  'InReview',
  'Done',
  'Blocked',
  'Abandoned',
] as const;

export type IssueStatus = (typeof ISSUE_STATUSES)[number];

export const ISSUE_PRIORITIES = ['Low', 'Medium', 'High', 'Critical'] as const;
export type IssuePriority = (typeof ISSUE_PRIORITIES)[number];

export interface Issue {
  id: string;
  title: string;
  description: string | null;
  status: IssueStatus;
  priority: IssuePriority;
  parent_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface IssueCreate {
  title: string;
  description?: string;
  priority?: IssuePriority;
  parent_id?: string;
}

export interface IssueTransition {
  status: IssueStatus;
}

export const COLUMN_ORDER: IssueStatus[] = [
  'Backlog',
  'Ready',
  'InProgress',
  'InReview',
  'Done',
  'Blocked',
  'Abandoned',
];

export const COLUMN_LABELS: Record<IssueStatus, string> = {
  Backlog: '백로그',
  Ready: '준비',
  InProgress: '진행 중',
  InReview: '리뷰 중',
  Done: '완료',
  Blocked: '차단됨',
  Abandoned: '포기',
};

export const PRIORITY_COLORS: Record<IssuePriority, string> = {
  Low: '#6b7280',
  Medium: '#3b82f6',
  High: '#f59e0b',
  Critical: '#ef4444',
};
