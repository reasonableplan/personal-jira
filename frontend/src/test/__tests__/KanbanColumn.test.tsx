import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { KanbanColumn } from '@/components/KanbanColumn';
import { DndContext } from '@dnd-kit/core';
import type { Issue } from '@/types/issue';

const MOCK_ISSUES: Issue[] = [
  {
    id: 'c-1',
    title: 'Task One',
    description: null,
    status: 'Backlog',
    priority: 'Low',
    parent_id: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 'c-2',
    title: 'Task Two',
    description: null,
    status: 'Backlog',
    priority: 'Medium',
    parent_id: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
];

const renderWithDnd = (ui: React.ReactElement) =>
  render(<DndContext>{ui}</DndContext>);

describe('KanbanColumn', () => {
  it('renders column label', () => {
    renderWithDnd(<KanbanColumn status="Backlog" issues={MOCK_ISSUES} />);
    expect(screen.getByText('백로그')).toBeInTheDocument();
  });

  it('renders issue count', () => {
    renderWithDnd(<KanbanColumn status="Backlog" issues={MOCK_ISSUES} />);
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('renders all issue cards', () => {
    renderWithDnd(<KanbanColumn status="Backlog" issues={MOCK_ISSUES} />);
    expect(screen.getByText('Task One')).toBeInTheDocument();
    expect(screen.getByText('Task Two')).toBeInTheDocument();
  });

  it('renders empty column', () => {
    renderWithDnd(<KanbanColumn status="Done" issues={[]} />);
    expect(screen.getByText('완료')).toBeInTheDocument();
    expect(screen.getByText('0')).toBeInTheDocument();
  });

  it('has droppable container', () => {
    renderWithDnd(<KanbanColumn status="Ready" issues={[]} />);
    expect(screen.getByTestId('column-Ready')).toBeInTheDocument();
  });
});
