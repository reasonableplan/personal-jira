export interface TimelineIssue {
  id: string;
  title: string;
  epicId: string;
  epicTitle: string;
  status: string;
  priority: string;
  startDate: string;
  dueDate: string;
}

export interface EpicGroup {
  epicId: string;
  epicTitle: string;
  startDate: string;
  endDate: string;
  issues: TimelineIssue[];
}

export interface TimelineDay {
  date: string;
  label: string;
  isWeekend: boolean;
}

export interface BarPosition {
  left: number;
  width: number;
}

export interface UseTimelineResult {
  epicGroups: EpicGroup[];
  timelineStart: string;
  totalDays: number;
  isLoading: boolean;
  error: string | null;
}
