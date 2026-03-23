import { describe, it, expect } from 'vitest';
import {
  calcDaysBetween,
  calcBarPosition,
  buildTimelineDays,
  groupIssuesByEpic,
  getStatusColor,
  GANTT_CONFIG,
} from '../gantt-utils';
import type { TimelineIssue } from '../types';

describe('calcDaysBetween', () => {
  it('returns 0 for same day', () => {
    expect(calcDaysBetween('2026-03-01', '2026-03-01')).toBe(0);
  });

  it('returns positive days for later end', () => {
    expect(calcDaysBetween('2026-03-01', '2026-03-05')).toBe(4);
  });

  it('returns negative days for earlier end', () => {
    expect(calcDaysBetween('2026-03-05', '2026-03-01')).toBe(-4);
  });
});

describe('calcBarPosition', () => {
  const timelineStart = '2026-03-01';

  it('calculates left offset and width', () => {
    const result = calcBarPosition('2026-03-03', '2026-03-06', timelineStart);
    expect(result.left).toBe(2 * GANTT_CONFIG.DAY_WIDTH);
    expect(result.width).toBe(3 * GANTT_CONFIG.DAY_WIDTH);
  });

  it('returns minimum width of 1 day for same-day tasks', () => {
    const result = calcBarPosition('2026-03-03', '2026-03-03', timelineStart);
    expect(result.width).toBe(GANTT_CONFIG.DAY_WIDTH);
  });

  it('clamps left to 0 when start is before timeline', () => {
    const result = calcBarPosition('2026-02-28', '2026-03-03', timelineStart);
    expect(result.left).toBe(0);
    expect(result.width).toBe(2 * GANTT_CONFIG.DAY_WIDTH);
  });
});

describe('buildTimelineDays', () => {
  it('generates correct day entries', () => {
    const days = buildTimelineDays('2026-03-01', 3);
    expect(days).toHaveLength(3);
    expect(days[0]).toEqual({ date: '2026-03-01', label: '3/1', isWeekend: true });
    expect(days[1]).toEqual({ date: '2026-03-02', label: '3/2', isWeekend: false });
    expect(days[2]).toEqual({ date: '2026-03-03', label: '3/3', isWeekend: false });
  });

  it('returns empty array for 0 days', () => {
    expect(buildTimelineDays('2026-03-01', 0)).toEqual([]);
  });
});

describe('groupIssuesByEpic', () => {
  const issues: TimelineIssue[] = [
    { id: '1', title: 'Task A', epicId: 'e1', epicTitle: 'Epic 1', status: 'IN_PROGRESS', priority: 'HIGH', startDate: '2026-03-01', dueDate: '2026-03-05' },
    { id: '2', title: 'Task B', epicId: 'e1', epicTitle: 'Epic 1', status: 'TODO', priority: 'MEDIUM', startDate: '2026-03-03', dueDate: '2026-03-07' },
    { id: '3', title: 'Task C', epicId: 'e2', epicTitle: 'Epic 2', status: 'DONE', priority: 'LOW', startDate: '2026-03-02', dueDate: '2026-03-04' },
  ];

  it('groups issues by epicId', () => {
    const groups = groupIssuesByEpic(issues);
    expect(groups).toHaveLength(2);
    expect(groups[0].epicId).toBe('e1');
    expect(groups[0].issues).toHaveLength(2);
    expect(groups[1].epicId).toBe('e2');
    expect(groups[1].issues).toHaveLength(1);
  });

  it('calculates epic date range from child issues', () => {
    const groups = groupIssuesByEpic(issues);
    expect(groups[0].startDate).toBe('2026-03-01');
    expect(groups[0].endDate).toBe('2026-03-07');
  });

  it('returns empty array for no issues', () => {
    expect(groupIssuesByEpic([])).toEqual([]);
  });
});

describe('getStatusColor', () => {
  it('returns correct color for each status', () => {
    expect(getStatusColor('DONE')).toBe('bg-green-500');
    expect(getStatusColor('IN_PROGRESS')).toBe('bg-blue-500');
    expect(getStatusColor('TODO')).toBe('bg-gray-400');
    expect(getStatusColor('BACKLOG')).toBe('bg-gray-300');
    expect(getStatusColor('UNKNOWN_STATUS')).toBe('bg-gray-300');
  });
});
