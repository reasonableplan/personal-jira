export const ISSUE_STATUSES = ['backlog', 'ready', 'in_progress', 'in_review', 'done', 'cancelled', 'blocked'] as const;
export type IssueStatus = (typeof ISSUE_STATUSES)[number];

export const ISSUE_PRIORITIES = ['low', 'medium', 'high', 'critical'] as const;
export type IssuePriority = (typeof ISSUE_PRIORITIES)[number];

export const ISSUE_TYPES = ['task', 'bug', 'story', 'epic'] as const;
export type IssueType = (typeof ISSUE_TYPES)[number];

export const TRANSITION_MATRIX: Record<IssueStatus, readonly IssueStatus[]> = {
  backlog: ['ready', 'cancelled'],
  ready: ['in_progress', 'backlog', 'cancelled'],
  in_progress: ['in_review', 'blocked', 'cancelled'],
  in_review: ['done', 'in_progress', 'cancelled'],
  done: [],
  cancelled: [],
  blocked: ['in_progress', 'cancelled'],
} as const;

export interface Issue {
  id: string;
  title: string;
  description: string | null;
  status: IssueStatus;
  priority: IssuePriority;
  issue_type: IssueType;
  parent_id: string | null;
  deleted_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface IssueCreate {
  title: string;
  description?: string;
  priority: IssuePriority;
  issue_type: IssueType;
  parent_id?: string;
}

export interface IssueUpdate {
  title?: string;
  description?: string;
  status?: IssueStatus;
  priority?: IssuePriority;
}

export interface IssueListParams {
  offset: number;
  limit: number;
  status?: IssueStatus;
  priority?: IssuePriority;
  issue_type?: IssueType;
  parent_id?: string;
}

export interface IssueListResponse {
  items: Issue[];
  total: number;
  offset: number;
  limit: number;
}

export interface IssueDependency {
  blocker_id: string;
  blocked_id: string;
  created_at: string;
}

export interface DependencyResponse {
  blocked_by: IssueDependency[];
  blocks: IssueDependency[];
}

export interface IssueDetailResponse extends Issue {
  children: Issue[];
  dependencies: DependencyResponse;
}

export interface TransitionRequest {
  status: IssueStatus;
}

export interface DependencyCreate {
  blocked_by_issue_id: string;
}
