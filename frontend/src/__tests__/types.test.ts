import { describe, it, expect, expectTypeOf } from 'vitest';
import type {
  Epic,
  Story,
  Task,
  Activity,
  Label,
  Agent,
  BoardColumn,
  PaginatedResponse,
  TaskPriority,
  TaskStatus,
  EpicStatus,
  StoryStatus,
  ActionType,
} from '@/types';

describe('Type Definitions', () => {
  it('Epic has required fields', () => {
    const epic: Epic = {
      id: '123',
      title: 'Test',
      description: null,
      status: 'active',
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    };
    expect(epic.id).toBe('123');
    expect(epic.status).toBe('active');
  });

  it('Story has required fields', () => {
    const story: Story = {
      id: '1',
      epic_id: '2',
      title: 'Test',
      description: null,
      status: 'active',
      sort_order: 0,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    };
    expect(story.epic_id).toBe('2');
  });

  it('Task has required fields', () => {
    const task: Task = {
      id: '1',
      story_id: '2',
      title: 'Test',
      description: null,
      status: 'backlog',
      board_column: 'Backlog',
      assigned_agent: null,
      priority: 'medium',
      labels: [],
      dependencies: [],
      retry_count: 0,
      created_at: '2026-01-01T00:00:00Z',
      started_at: null,
      completed_at: null,
    };
    expect(task.board_column).toBe('Backlog');
  });

  it('Activity has required fields', () => {
    const activity: Activity = {
      id: '1',
      task_id: '2',
      actor: 'user',
      action_type: 'comment',
      content: { message: 'hello' },
      created_at: '2026-01-01T00:00:00Z',
    };
    expect(activity.action_type).toBe('comment');
  });

  it('Label has required fields', () => {
    const label: Label = { id: '1', name: 'bug', color: '#FF0000' };
    expect(label.color).toBe('#FF0000');
  });

  it('Agent has required fields', () => {
    const agent: Agent = {
      id: '1',
      name: 'bot',
      domain: 'backend',
      status: 'idle',
      last_heartbeat: '2026-01-01T00:00:00Z',
    };
    expect(agent.status).toBe('idle');
  });

  it('PaginatedResponse has items and total', () => {
    const res: PaginatedResponse<Epic> = {
      items: [],
      total: 0,
      page: 1,
      per_page: 20,
    };
    expect(res.total).toBe(0);
  });

  it('EpicStatus values are correct', () => {
    const statuses: EpicStatus[] = ['active', 'completed', 'archived'];
    expect(statuses).toHaveLength(3);
  });

  it('TaskStatus values are correct', () => {
    const statuses: TaskStatus[] = ['backlog', 'ready', 'in-progress', 'review', 'done', 'failed'];
    expect(statuses).toHaveLength(6);
  });

  it('BoardColumn values are correct', () => {
    const cols: BoardColumn[] = ['Backlog', 'Ready', 'In Progress', 'Review', 'Done'];
    expect(cols).toHaveLength(5);
  });

  it('TaskPriority values are correct', () => {
    const priorities: TaskPriority[] = ['low', 'medium', 'high', 'critical'];
    expect(priorities).toHaveLength(4);
  });

  it('ActionType values are correct', () => {
    const types: ActionType[] = ['status_change', 'comment', 'review_feedback', 'code_change'];
    expect(types).toHaveLength(4);
  });
});
