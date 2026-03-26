export const EPIC_STATUS = {
  PLANNING: 'planning',
  ACTIVE: 'active',
  DONE: 'done',
} as const;

export type EpicStatus = (typeof EPIC_STATUS)[keyof typeof EPIC_STATUS];

export interface Epic {
  id: string;
  title: string;
  description: string | null;
  status: EpicStatus;
  created_at: string;
  updated_at: string;
}

export interface CreateEpicRequest {
  title: string;
  description?: string | null;
}

export interface UpdateEpicRequest {
  title?: string;
  description?: string | null;
  status?: EpicStatus;
}
