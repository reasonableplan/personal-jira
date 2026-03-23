import {
  IssueType,
  IssuePriority,
  IssueStatus,
  ISSUE_TYPE_LABELS,
  ISSUE_PRIORITY_LABELS,
  ISSUE_STATUS_LABELS,
  type Issue,
  type IssueFormData,
} from '../../types/issue';

describe('Issue types', () => {
  test('IssueType has 5 values', () => {
    expect(Object.values(IssueType)).toHaveLength(5);
  });

  test('IssuePriority has 5 values', () => {
    expect(Object.values(IssuePriority)).toHaveLength(5);
  });

  test('IssueStatus has 7 values', () => {
    expect(Object.values(IssueStatus)).toHaveLength(7);
  });

  test('all IssueType values have labels', () => {
    for (const t of Object.values(IssueType)) {
      expect(ISSUE_TYPE_LABELS[t]).toBeDefined();
    }
  });

  test('all IssuePriority values have labels', () => {
    for (const p of Object.values(IssuePriority)) {
      expect(ISSUE_PRIORITY_LABELS[p]).toBeDefined();
    }
  });

  test('all IssueStatus values have labels', () => {
    for (const s of Object.values(IssueStatus)) {
      expect(ISSUE_STATUS_LABELS[s]).toBeDefined();
    }
  });

  test('IssueFormData has required fields', () => {
    const form: IssueFormData = {
      title: 'Test',
      description: '',
      issue_type: IssueType.TASK,
      priority: IssuePriority.MEDIUM,
      labels: [],
    };
    expect(form.title).toBe('Test');
    expect(form.issue_type).toBe(IssueType.TASK);
  });

  test('Issue extends IssueFormData with id and status', () => {
    const issue: Issue = {
      id: 'uuid-1',
      title: 'Bug',
      description: '# Heading',
      issue_type: IssueType.BUG,
      priority: IssuePriority.HIGH,
      labels: ['frontend'],
      status: IssueStatus.BACKLOG,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    };
    expect(issue.id).toBe('uuid-1');
    expect(issue.status).toBe(IssueStatus.BACKLOG);
  });
});
