import { describe, it, expect } from 'vitest';
import {
  ISSUE_STATUSES,
  COLUMN_ORDER,
  COLUMN_LABELS,
  PRIORITY_COLORS,
  ISSUE_PRIORITIES,
} from '@/types/issue';
import type { IssueStatus, IssuePriority, Issue } from '@/types/issue';

describe('Issue Types', () => {
  it('defines 7 issue statuses', () => {
    expect(ISSUE_STATUSES).toHaveLength(7);
  });

  it('includes all expected statuses', () => {
    const expected: IssueStatus[] = [
      'Backlog', 'Ready', 'InProgress', 'InReview', 'Done', 'Blocked', 'Abandoned',
    ];
    expect([...ISSUE_STATUSES]).toEqual(expected);
  });

  it('COLUMN_ORDER matches ISSUE_STATUSES', () => {
    expect(COLUMN_ORDER).toEqual([...ISSUE_STATUSES]);
  });

  it('COLUMN_LABELS has entry for every status', () => {
    for (const status of ISSUE_STATUSES) {
      expect(COLUMN_LABELS[status]).toBeDefined();
      expect(typeof COLUMN_LABELS[status]).toBe('string');
    }
  });

  it('defines 4 priorities', () => {
    expect(ISSUE_PRIORITIES).toHaveLength(4);
  });

  it('PRIORITY_COLORS has entry for every priority', () => {
    for (const priority of ISSUE_PRIORITIES) {
      expect(PRIORITY_COLORS[priority]).toBeDefined();
    }
  });

  it('Issue type has required fields', () => {
    const issue: Issue = {
      id: 'test-id',
      title: 'Test',
      description: null,
      status: 'Backlog',
      priority: 'Medium',
      parent_id: null,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    };
    expect(issue.id).toBe('test-id');
    expect(issue.status).toBe('Backlog');
  });
});
