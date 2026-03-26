export const STORY_STATUS = {
  TODO: 'todo',
  IN_PROGRESS: 'in_progress',
  DONE: 'done',
} as const;

export type StoryStatus = (typeof STORY_STATUS)[keyof typeof STORY_STATUS];

export interface Story {
  id: string;
  epic_id: string;
  title: string;
  description: string | null;
  status: StoryStatus;
  priority: number;
  created_at: string;
  updated_at: string;
}

export interface CreateStoryRequest {
  epic_id: string;
  title: string;
  description?: string | null;
  priority?: number;
}

export interface UpdateStoryRequest {
  title?: string;
  description?: string | null;
  status?: StoryStatus;
  priority?: number;
}
