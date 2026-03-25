import { describe, it, expectTypeOf } from 'vitest';
import type { Epic, Story, Task, Activity, Label, Agent, BoardColumn } from '@/types';

describe('API type definitions', () => {
  it('Epic has required fields', () => {
    expectTypeOf<Epic>().toHaveProperty('id');
    expectTypeOf<Epic>().toHaveProperty('title');
    expectTypeOf<Epic>().toHaveProperty('description');
    expectTypeOf<Epic>().toHaveProperty('status');
    expectTypeOf<Epic>().toHaveProperty('created_at');
    expectTypeOf<Epic>().toHaveProperty('updated_at');
  });

  it('Story has required fields', () => {
    expectTypeOf<Story>().toHaveProperty('id');
    expectTypeOf<Story>().toHaveProperty('epic_id');
    expectTypeOf<Story>().toHaveProperty('title');
    expectTypeOf<Story>().toHaveProperty('sort_order');
  });

  it('Task has required fields', () => {
    expectTypeOf<Task>().toHaveProperty('id');
    expectTypeOf<Task>().toHaveProperty('story_id');
    expectTypeOf<Task>().toHaveProperty('title');
    expectTypeOf<Task>().toHaveProperty('status');
    expectTypeOf<Task>().toHaveProperty('board_column');
    expectTypeOf<Task>().toHaveProperty('priority');
    expectTypeOf<Task>().toHaveProperty('labels');
    expectTypeOf<Task>().toHaveProperty('dependencies');
    expectTypeOf<Task>().toHaveProperty('retry_count');
  });

  it('Activity has required fields', () => {
    expectTypeOf<Activity>().toHaveProperty('id');
    expectTypeOf<Activity>().toHaveProperty('task_id');
    expectTypeOf<Activity>().toHaveProperty('actor');
    expectTypeOf<Activity>().toHaveProperty('action_type');
    expectTypeOf<Activity>().toHaveProperty('content');
  });

  it('Label has required fields', () => {
    expectTypeOf<Label>().toHaveProperty('id');
    expectTypeOf<Label>().toHaveProperty('name');
    expectTypeOf<Label>().toHaveProperty('color');
  });

  it('Agent has required fields', () => {
    expectTypeOf<Agent>().toHaveProperty('id');
    expectTypeOf<Agent>().toHaveProperty('name');
    expectTypeOf<Agent>().toHaveProperty('domain');
    expectTypeOf<Agent>().toHaveProperty('status');
    expectTypeOf<Agent>().toHaveProperty('last_heartbeat');
  });

  it('BoardColumn has correct structure', () => {
    expectTypeOf<BoardColumn>().toHaveProperty('name');
    expectTypeOf<BoardColumn>().toHaveProperty('tasks');
  });
});
