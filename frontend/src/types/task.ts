import type { Label } from '@/types/label';

export const TASK_STATUS = {
  TODO: 'todo',
  IN_PROGRESS: 'in_progress',
  IN_REVIEW: 'in_review',
  DONE: 'done',
} as const;

export type TaskStatus = (typeof TASK_STATUS)[keyof typeof TASK_STATUS];

export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
  [TASK_STATUS.TODO]: 'To Do',
  [TASK_STATUS.IN_PROGRESS]: 'In Progress',
  [TASK_STATUS.IN_REVIEW]: 'In Review',
  [TASK_STATUS.DONE]: 'Done',
};

export interface Task {
  id: string;
  story_id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: number;
  labels: Label[];
  created_at: string;
  updated_at: string;
}

export interface CreateTaskRequest {
  story_id: string;
  title: string;
  description?: string | null;
  priority?: number;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string | null;
  status?: TaskStatus;
  priority?: number;
}

export interface UpdateTaskStatusRequest {
  status: TaskStatus;
}

export interface TaskFilters {
  status?: TaskStatus;
  priority?: number;
  label?: string;
  search?: string;
  story_id?: string;
}
