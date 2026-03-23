import { IssuePriority, IssueStatus, IssueType } from '../types/issue';

export const DEFAULT_PAGE_SIZE = 20;
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100] as const;

export const STATUS_LABELS: Record<IssueStatus, string> = {
  [IssueStatus.BACKLOG]: 'Backlog',
  [IssueStatus.TODO]: 'To Do',
  [IssueStatus.IN_PROGRESS]: 'In Progress',
  [IssueStatus.IN_REVIEW]: 'In Review',
  [IssueStatus.DONE]: 'Done',
  [IssueStatus.CANCELLED]: 'Cancelled',
};

export const PRIORITY_LABELS: Record<IssuePriority, string> = {
  [IssuePriority.CRITICAL]: 'Critical',
  [IssuePriority.HIGH]: 'High',
  [IssuePriority.MEDIUM]: 'Medium',
  [IssuePriority.LOW]: 'Low',
};

export const TYPE_LABELS: Record<IssueType, string> = {
  [IssueType.EPIC]: 'Epic',
  [IssueType.STORY]: 'Story',
  [IssueType.TASK]: 'Task',
  [IssueType.BUG]: 'Bug',
  [IssueType.SUBTASK]: 'Subtask',
};

export const PRIORITY_ORDER: Record<IssuePriority, number> = {
  [IssuePriority.CRITICAL]: 0,
  [IssuePriority.HIGH]: 1,
  [IssuePriority.MEDIUM]: 2,
  [IssuePriority.LOW]: 3,
};

export const STATUS_COLOR: Record<IssueStatus, string> = {
  [IssueStatus.BACKLOG]: 'bg-gray-100 text-gray-700',
  [IssueStatus.TODO]: 'bg-blue-100 text-blue-700',
  [IssueStatus.IN_PROGRESS]: 'bg-yellow-100 text-yellow-700',
  [IssueStatus.IN_REVIEW]: 'bg-purple-100 text-purple-700',
  [IssueStatus.DONE]: 'bg-green-100 text-green-700',
  [IssueStatus.CANCELLED]: 'bg-red-100 text-red-700',
};

export const PRIORITY_COLOR: Record<IssuePriority, string> = {
  [IssuePriority.CRITICAL]: 'bg-red-100 text-red-700',
  [IssuePriority.HIGH]: 'bg-orange-100 text-orange-700',
  [IssuePriority.MEDIUM]: 'bg-yellow-100 text-yellow-700',
  [IssuePriority.LOW]: 'bg-gray-100 text-gray-700',
};
