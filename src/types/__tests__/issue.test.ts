import type { Issue, IssueCreate, IssueUpdate, IssueStatus, IssuePriority, IssueType, IssueListResponse, IssueDetailResponse, IssueDependency, DependencyResponse, TransitionRequest, DependencyCreate } from '../issue';
import { ISSUE_STATUSES, ISSUE_PRIORITIES, ISSUE_TYPES, TRANSITION_MATRIX } from '../issue';

describe('Issue type constants', () => {
  it('has 7 issue statuses', () => {
    expect(ISSUE_STATUSES).toHaveLength(7);
    expect(ISSUE_STATUSES).toContain('backlog');
    expect(ISSUE_STATUSES).toContain('ready');
    expect(ISSUE_STATUSES).toContain('in_progress');
    expect(ISSUE_STATUSES).toContain('in_review');
    expect(ISSUE_STATUSES).toContain('done');
    expect(ISSUE_STATUSES).toContain('cancelled');
    expect(ISSUE_STATUSES).toContain('blocked');
  });

  it('has 4 priorities', () => {
    expect(ISSUE_PRIORITIES).toHaveLength(4);
    expect(ISSUE_PRIORITIES).toContain('low');
    expect(ISSUE_PRIORITIES).toContain('medium');
    expect(ISSUE_PRIORITIES).toContain('high');
    expect(ISSUE_PRIORITIES).toContain('critical');
  });

  it('has 4 issue types', () => {
    expect(ISSUE_TYPES).toHaveLength(4);
    expect(ISSUE_TYPES).toContain('task');
    expect(ISSUE_TYPES).toContain('bug');
    expect(ISSUE_TYPES).toContain('story');
    expect(ISSUE_TYPES).toContain('epic');
  });
});

describe('TRANSITION_MATRIX', () => {
  it('allows backlog to transition to ready and cancelled', () => {
    expect(TRANSITION_MATRIX.backlog).toContain('ready');
    expect(TRANSITION_MATRIX.backlog).toContain('cancelled');
  });

  it('allows ready to transition to in_progress and backlog', () => {
    expect(TRANSITION_MATRIX.ready).toContain('in_progress');
    expect(TRANSITION_MATRIX.ready).toContain('backlog');
  });

  it('allows in_progress to transition to in_review and blocked', () => {
    expect(TRANSITION_MATRIX.in_progress).toContain('in_review');
    expect(TRANSITION_MATRIX.in_progress).toContain('blocked');
  });

  it('allows in_review to transition to done and in_progress', () => {
    expect(TRANSITION_MATRIX.in_review).toContain('done');
    expect(TRANSITION_MATRIX.in_review).toContain('in_progress');
  });

  it('done has no transitions', () => {
    expect(TRANSITION_MATRIX.done).toHaveLength(0);
  });

  it('cancelled has no transitions', () => {
    expect(TRANSITION_MATRIX.cancelled).toHaveLength(0);
  });

  it('allows blocked to transition to in_progress and cancelled', () => {
    expect(TRANSITION_MATRIX.blocked).toContain('in_progress');
    expect(TRANSITION_MATRIX.blocked).toContain('cancelled');
  });
});

describe('Type shape validation', () => {
  it('IssueCreate requires title, priority, issue_type', () => {
    const create: IssueCreate = { title: 'Test', priority: 'medium', issue_type: 'task' };
    expect(create.title).toBe('Test');
    expect(create.priority).toBe('medium');
    expect(create.issue_type).toBe('task');
  });

  it('IssueCreate allows optional description and parent_id', () => {
    const create: IssueCreate = { title: 'Test', priority: 'high', issue_type: 'bug', description: 'desc', parent_id: 'uuid' };
    expect(create.description).toBe('desc');
    expect(create.parent_id).toBe('uuid');
  });

  it('IssueUpdate has all fields optional', () => {
    const update: IssueUpdate = {};
    expect(update.title).toBeUndefined();
    const partial: IssueUpdate = { title: 'new' };
    expect(partial.title).toBe('new');
  });

  it('Issue has required id, title, status, timestamps', () => {
    const issue: Issue = {
      id: 'uuid-1', title: 'Test', description: null, status: 'backlog',
      priority: 'medium', issue_type: 'task', parent_id: null,
      deleted_at: null, created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z',
    };
    expect(issue.id).toBe('uuid-1');
  });

  it('IssueListResponse has items, total, offset, limit', () => {
    const list: IssueListResponse = { items: [], total: 0, offset: 0, limit: 20 };
    expect(list.total).toBe(0);
  });

  it('IssueDetailResponse extends Issue with children and dependencies', () => {
    const detail: IssueDetailResponse = {
      id: 'uuid-1', title: 'Test', description: null, status: 'backlog',
      priority: 'medium', issue_type: 'task', parent_id: null,
      deleted_at: null, created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z',
      children: [], dependencies: { blocked_by: [], blocks: [] },
    };
    expect(detail.children).toEqual([]);
  });
});
