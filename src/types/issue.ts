export type IssueStatus = 'BACKLOG' | 'TODO' | 'IN_PROGRESS' | 'IN_REVIEW' | 'DONE' | 'CANCELLED' | 'BLOCKED';
export type IssuePriority = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type IssueType = 'TASK' | 'BUG' | 'FEATURE' | 'EPIC';

export interface Issue {
  id: string;
  title: string;
  description: string;
  status: IssueStatus;
  priority: IssuePriority;
  issue_type: IssueType;
  assignee_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: string;
  issue_id: string;
  author: string;
  content: string;
  created_at: string;
}

export interface ActivityLog {
  id: string;
  issue_id: string;
  action: string;
  actor: string;
  detail: string;
  created_at: string;
}

export interface Artifact {
  id: string;
  issue_id: string;
  filename: string;
  url: string;
  size_bytes: number;
  uploaded_at: string;
}
