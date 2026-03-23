export const ISSUE_STATUSES = [
  'Backlog',
  'Ready',
  'InProgress',
  'InReview',
  'Done',
  'Blocked',
  'Cancelled',
] as const;

export type IssueStatus = (typeof ISSUE_STATUSES)[number];

export interface StatusCount {
  status: IssueStatus;
  count: number;
}

export interface AgentStats {
  agentId: string;
  name: string;
  totalIssues: number;
  completedIssues: number;
  inProgressIssues: number;
  avgCompletionTimeMinutes: number;
  completionRate: number;
}

export interface DashboardData {
  statusCounts: StatusCount[];
  agentStats: AgentStats[];
  totalIssues: number;
  completedIssues: number;
  completionRate: number;
}

export const STATUS_COLORS: Record<IssueStatus, string> = {
  Backlog: '#94a3b8',
  Ready: '#60a5fa',
  InProgress: '#fbbf24',
  InReview: '#a78bfa',
  Done: '#34d399',
  Blocked: '#f87171',
  Cancelled: '#6b7280',
};
