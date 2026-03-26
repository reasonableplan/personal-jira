import type { EpicStatus } from '@/types/epic';
import type { TaskStatus } from '@/types/task';

export interface DashboardSummary {
  total_epics: number;
  total_stories: number;
  total_tasks: number;
  tasks_by_status: Record<TaskStatus, number>;
  completion_rate: number;
  epics_summary: EpicSummary[];
  recent_activities: RecentActivity[];
}

export interface EpicSummary {
  id: string;
  title: string;
  status: EpicStatus;
  total_tasks: number;
  completed_tasks: number;
  completion_rate: number;
}

export interface RecentActivity {
  entity_type: string;
  entity_id: string;
  entity_title: string;
  action: string;
  detail: string;
  timestamp: string;
}
