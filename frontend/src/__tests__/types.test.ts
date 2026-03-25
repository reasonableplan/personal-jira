import { describe, it, expect } from 'vitest';
import type { Epic, Story, Task, Activity, Label, Agent, BoardColumn } from '../types';

describe('Type definitions', () => {
  it('Epic type matches API spec', () => {
    const epic: Epic = {
      id: '123',
      title: 'Test',
      description: null,
      status: 'active',
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    };
    expect(epic.status).toBe('active');
  });

  it('Story type matches API spec', () => {
    const story: Story = {
      id: '123',
      epic_id: '456',
      title: 'Test',
      description: null,
      status: 'active',
      sort_order: 0,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    };
    expect(story.status).toBe('active');
  });

  it('Task type matches API spec', () => {
    const task: Task = {
      id: '123',
      story_id: '456',
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
    expect(task.priority).toBe('medium');
  });

  it('Activity type matches API spec', () => {
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

  it('Label type matches API spec', () => {
    const label: Label = { id: '1', name: 'bug', color: '#FF0000' };
    expect(label.color).toBe('#FF0000');
  });

  it('Agent type matches API spec', () => {
    const agent: Agent = {
      id: '1',
      name: 'Agent',
      domain: 'backend',
      status: 'idle',
      last_heartbeat: '2026-01-01T00:00:00Z',
    };
    expect(agent.status).toBe('idle');
  });

  it('BoardColumn type covers all columns', () => {
    const columns: BoardColumn[] = ['Backlog', 'Ready', 'In Progress', 'Review', 'Done'];
    expect(columns).toHaveLength(5);
  });
});
