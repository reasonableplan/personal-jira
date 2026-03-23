export enum IssueType {
  TASK = 'task',
  BUG = 'bug',
  STORY = 'story',
  EPIC = 'epic',
  SUBTASK = 'subtask',
}

export enum IssuePriority {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
  TRIVIAL = 'trivial',
}

export enum IssueStatus {
  BACKLOG = 'backlog',
  READY = 'ready',
  IN_PROGRESS = 'in_progress',
  IN_REVIEW = 'in_review',
  DONE = 'done',
  BLOCKED = 'blocked',
  CANCELLED = 'cancelled',
}

export const ISSUE_TYPE_LABELS: Record<IssueType, string> = {
  [IssueType.TASK]: 'Task',
  [IssueType.BUG]: 'Bug',
  [IssueType.STORY]: 'Story',
  [IssueType.EPIC]: 'Epic',
  [IssueType.SUBTASK]: 'Subtask',
};

export const ISSUE_PRIORITY_LABELS: Record<IssuePriority, string> = {
  [IssuePriority.CRITICAL]: 'Critical',
  [IssuePriority.HIGH]: 'High',
  [IssuePriority.MEDIUM]: 'Medium',
  [IssuePriority.LOW]: 'Low',
  [IssuePriority.TRIVIAL]: 'Trivial',
};

export const ISSUE_STATUS_LABELS: Record<IssueStatus, string> = {
  [IssueStatus.BACKLOG]: 'Backlog',
  [IssueStatus.READY]: 'Ready',
  [IssueStatus.IN_PROGRESS]: 'In Progress',
  [IssueStatus.IN_REVIEW]: 'In Review',
  [IssueStatus.DONE]: 'Done',
  [IssueStatus.BLOCKED]: 'Blocked',
  [IssueStatus.CANCELLED]: 'Cancelled',
};

export const TITLE_MAX_LENGTH = 200;

export interface IssueFormData {
  title: string;
  description: string;
  issue_type: IssueType;
  priority: IssuePriority;
  labels: string[];
}

export interface Issue extends IssueFormData {
  id: string;
  status: IssueStatus;
  created_at: string;
  updated_at: string;
}

export const DEFAULT_FORM_DATA: IssueFormData = {
  title: '',
  description: '',
  issue_type: IssueType.TASK,
  priority: IssuePriority.MEDIUM,
  labels: [],
};
