import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { KanbanBoard } from '../KanbanBoard';
import { MOCK_ISSUES } from '@/test/fixtures';
import { ISSUE_STATUS, STATUS_LABELS, KANBAN_COLUMNS } from '@/types/issue';
import type { Issue } from '@/types/issue';

describe('KanbanBoard', () => {
  const defaultProps = {
    issues: MOCK_ISSUES,
    onIssueClick: vi.fn(),
    onStatusChange: vi.fn(),
  };

  it('renders all status columns', () => {
    render(<KanbanBoard {...defaultProps} />);
    for (const status of KANBAN_COLUMNS) {
      expect(screen.getByText(STATUS_LABELS[status])).toBeInTheDocument();
    }
  });

  it('renders issues in correct columns', () => {
    render(<KanbanBoard {...defaultProps} />);
    const todoColumn = screen.getByTestId(`column-${ISSUE_STATUS.TODO}`);
    expect(within(todoColumn).getByText('Set up CI pipeline')).toBeInTheDocument();

    const inProgressColumn = screen.getByTestId(`column-${ISSUE_STATUS.IN_PROGRESS}`);
    expect(within(inProgressColumn).getByText('Write API docs')).toBeInTheDocument();

    const doneColumn = screen.getByTestId(`column-${ISSUE_STATUS.DONE}`);
    expect(within(doneColumn).getByText('Fix login bug')).toBeInTheDocument();
  });

  it('displays issue count per column', () => {
    render(<KanbanBoard {...defaultProps} />);
    const todoColumn = screen.getByTestId(`column-${ISSUE_STATUS.TODO}`);
    expect(within(todoColumn).getByTestId('issue-count')).toHaveTextContent('1');
  });

  it('calls onIssueClick when an issue card is clicked', async () => {
    const user = userEvent.setup();
    render(<KanbanBoard {...defaultProps} />);
    await user.click(screen.getByText('Set up CI pipeline'));
    expect(defaultProps.onIssueClick).toHaveBeenCalledWith(MOCK_ISSUES[0]);
  });

  it('shows priority badge on issue cards', () => {
    render(<KanbanBoard {...defaultProps} />);
    const todoColumn = screen.getByTestId(`column-${ISSUE_STATUS.TODO}`);
    expect(within(todoColumn).getByTestId('priority-badge')).toHaveTextContent('High');
  });

  it('shows assignee on issue cards when present', () => {
    render(<KanbanBoard {...defaultProps} />);
    expect(screen.getAllByText('alice').length).toBeGreaterThanOrEqual(1);
  });

  it('renders empty columns with no issues', () => {
    render(<KanbanBoard {...defaultProps} issues={[]} />);
    for (const status of KANBAN_COLUMNS) {
      const column = screen.getByTestId(`column-${status}`);
      expect(within(column).getByTestId('issue-count')).toHaveTextContent('0');
    }
  });

  it('renders empty state message when column has no issues', () => {
    render(<KanbanBoard {...defaultProps} issues={[]} />);
    const emptyMessages = screen.getAllByText('No issues');
    expect(emptyMessages).toHaveLength(KANBAN_COLUMNS.length);
  });

  it('applies correct data attribute for drag source', () => {
    render(<KanbanBoard {...defaultProps} />);
    const cards = screen.getAllByTestId('issue-card');
    expect(cards[0]).toHaveAttribute('data-issue-id', MOCK_ISSUES[0].id);
  });

  it('handles large number of issues without crashing', () => {
    const manyIssues: Issue[] = Array.from({ length: 100 }, (_, i) => ({
      id: `id-${i}`,
      title: `Issue ${i}`,
      description: '',
      status: KANBAN_COLUMNS[i % KANBAN_COLUMNS.length],
      priority: 'medium',
      assignee: null,
      parent_id: null,
      created_at: '2026-03-23T00:00:00Z',
      updated_at: '2026-03-23T00:00:00Z',
    }));
    render(<KanbanBoard {...defaultProps} issues={manyIssues} />);
    expect(screen.getAllByTestId('issue-card')).toHaveLength(100);
  });
});