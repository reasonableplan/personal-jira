export interface Epic {
  id: string;
  title: string;
  description: string | null;
  status: 'active' | 'completed' | 'archived';
  created_at: string;
  updated_at: string;
}

export interface Story {
  id: string;
  epic_id: string;
  title: string;
  description: string | null;
  status: 'active' | 'completed';
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  story_id: string;
  title: string;
  description: string | null;
  status: 'backlog' | 'ready' | 'in-progress' | 'review' | 'done' | 'failed';
  board_column: 'Backlog' | 'Ready' | 'In Progress' | 'Review' | 'Done';
  assigned_agent: string | null;
  priority: 'low' | 'medium' | 'high' | 'critical';
  labels: string[];
  dependencies: string[];
  retry_count: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface Activity {
  id: string;
  task_id: string;
  actor: string;
  action_type: 'status_change' | 'comment' | 'review_feedback' | 'code_change';
  content: Record<string, unknown>;
  created_at: string;
}

export interface Label {
  id: string;
  name: string;
  color: string;
}

export interface Agent {
  id: string;
  name: string;
  domain: string;
  status: 'idle' | 'busy' | 'offline';
  last_heartbeat: string;
}

export interface BoardColumn {
  name: 'Backlog' | 'Ready' | 'In Progress' | 'Review' | 'Done';
  tasks: Task[];
}

export interface BoardResponse {
  columns: BoardColumn[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}
