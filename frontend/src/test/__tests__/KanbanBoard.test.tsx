import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { KanbanBoard } from '@/components/KanbanBoard';
import { issueApi } from '@/services/api';
import type { Issue } from '@/types/issue';

vi.mock('@/services/api', () => ({
  issueApi: {
    list: vi.fn(),
    transition: vi.fn(),
  },
}));

const MOCK_ISSUES: Issue[] = [
  {
    id: 'b-1',
    title: 'Backlog Task',
    description: null,
    status: 'Backlog',
    priority: 'Low',
    parent_id: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 'b-2',
    title: 'Active Task',
    description: null,
    status: 'InProgress',
    priority: 'High',
    parent_id: null,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
];

describe('KanbanBoard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state', () => {
    vi.mocked(issueApi.list).mockReturnValue(new Promise(() => {}));
    render(<KanbanBoard />);
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('renders all columns after loading', async () => {
    vi.mocked(issueApi.list).mockResolvedValue(MOCK_ISSUES);
    render(<KanbanBoard />);

    await waitFor(() => {
      expect(screen.getByText('백로그')).toBeInTheDocument();
    });

    expect(screen.getByText('준비')).toBeInTheDocument();
    expect(screen.getByText('진행 중')).toBeInTheDocument();
    expect(screen.getByText('리뷰 중')).toBeInTheDocument();
    expect(screen.getByText('완료')).toBeInTheDocument();
    expect(screen.getByText('차단됨')).toBeInTheDocument();
    expect(screen.getByText('포기')).toBeInTheDocument();
  });

  it('renders issues in correct columns', async () => {
    vi.mocked(issueApi.list).mockResolvedValue(MOCK_ISSUES);
    render(<KanbanBoard />);

    await waitFor(() => {
      expect(screen.getByText('Backlog Task')).toBeInTheDocument();
    });

    expect(screen.getByText('Active Task')).toBeInTheDocument();
  });

  it('renders error state', async () => {
    vi.mocked(issueApi.list).mockRejectedValue(new Error('Server down'));
    render(<KanbanBoard />);

    await waitFor(() => {
      expect(screen.getByTestId('error-message')).toBeInTheDocument();
    });

    expect(screen.getByText(/Server down/)).toBeInTheDocument();
  });
});
