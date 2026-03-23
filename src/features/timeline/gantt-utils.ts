import type { TimelineIssue, EpicGroup, TimelineDay, BarPosition } from './types';

export const GANTT_CONFIG = {
  DAY_WIDTH: 40,
  ROW_HEIGHT: 36,
  HEADER_HEIGHT: 48,
  LABEL_WIDTH: 200,
  PADDING_DAYS: 2,
} as const;

export function calcDaysBetween(start: string, end: string): number {
  const s = new Date(start);
  const e = new Date(end);
  return Math.round((e.getTime() - s.getTime()) / (1000 * 60 * 60 * 24));
}

export function calcBarPosition(
  issueStart: string,
  issueDue: string,
  timelineStart: string,
): BarPosition {
  const offsetDays = calcDaysBetween(timelineStart, issueStart);
  const durationDays = calcDaysBetween(issueStart, issueDue);

  const clampedOffset = Math.max(0, offsetDays);
  const adjustedDuration = durationDays - (clampedOffset - offsetDays);
  const width = Math.max(1, adjustedDuration) * GANTT_CONFIG.DAY_WIDTH;

  return {
    left: clampedOffset * GANTT_CONFIG.DAY_WIDTH,
    width,
  };
}

export function buildTimelineDays(start: string, count: number): TimelineDay[] {
  const days: TimelineDay[] = [];
  const startDate = new Date(start);

  for (let i = 0; i < count; i++) {
    const d = new Date(startDate);
    d.setDate(d.getDate() + i);
    const dayOfWeek = d.getDay();
    days.push({
      date: d.toISOString().slice(0, 10),
      label: `${d.getMonth() + 1}/${d.getDate()}`,
      isWeekend: dayOfWeek === 0 || dayOfWeek === 6,
    });
  }

  return days;
}

export function groupIssuesByEpic(issues: TimelineIssue[]): EpicGroup[] {
  if (issues.length === 0) return [];

  const map = new Map<string, { epicTitle: string; issues: TimelineIssue[] }>();

  for (const issue of issues) {
    const existing = map.get(issue.epicId);
    if (existing) {
      existing.issues.push(issue);
    } else {
      map.set(issue.epicId, { epicTitle: issue.epicTitle, issues: [issue] });
    }
  }

  return Array.from(map.entries()).map(([epicId, { epicTitle, issues: groupIssues }]) => {
    const dates = groupIssues.flatMap((i) => [i.startDate, i.dueDate]).sort();
    return {
      epicId,
      epicTitle,
      startDate: dates[0],
      endDate: dates[dates.length - 1],
      issues: groupIssues,
    };
  });
}

const STATUS_COLORS: Record<string, string> = {
  DONE: 'bg-green-500',
  IN_PROGRESS: 'bg-blue-500',
  IN_REVIEW: 'bg-yellow-500',
  TODO: 'bg-gray-400',
  READY: 'bg-indigo-400',
  BLOCKED: 'bg-red-500',
  BACKLOG: 'bg-gray-300',
};

const DEFAULT_STATUS_COLOR = 'bg-gray-300';

export function getStatusColor(status: string): string {
  return STATUS_COLORS[status] ?? DEFAULT_STATUS_COLOR;
}
