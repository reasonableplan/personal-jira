import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { DashboardPage } from '../DashboardPage';
import * as useDashboardModule from '@/hooks/useDashboard';
import type { DashboardData } from '@/types/dashboard';

const MOCK_DASHBOARD: DashboardData = {
  totalIssues: 40,
  completedIssues: 15,
  completionRate: 37.5,
  statusCounts: [
    { status: 'Done', count: 15 },
    { status: 'InProgress', count: 5 },
    { status: 'Backlog', count: 10 },
    { status: 'Ready', count: 3 },
    { status: 'InReview', count: 2 },
    { status: 'Blocked', count: 1 },
    { status: 'Cancelled', count: 4 },
  ],
  agentStats: [
    {
      agentId: 'agent-001',
      name: 'agent-backend',
      totalIssues: 20,
      completedIssues: 15,
      inProgressIssues: 3,
      avgCompletionTimeMinutes: 12.5,
      completionRate: 75,
    },
  ],
};

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('shows loading state', () => {
    vi.spyOn(useDashboardModule, 'useDashboard').mockReturnValue({
      data: null,
      loading: true,
      error: null,
      refetch: vi.fn(),
    });
    render(<DashboardPage />);
    expect(screen.getByText('로딩 중...')).toBeInTheDocument();
  });

  it('shows error state', () => {
    vi.spyOn(useDashboardModule, 'useDashboard').mockReturnValue({
      data: null,
      loading: false,
      error: 'Network error',
      refetch: vi.fn(),
    });
    render(<DashboardPage />);
    expect(screen.getByText('Network error')).toBeInTheDocument();
  });

  it('renders dashboard title', () => {
    vi.spyOn(useDashboardModule, 'useDashboard').mockReturnValue({
      data: MOCK_DASHBOARD,
      loading: false,
      error: null,
      refetch: vi.fn(),
    });
    render(<DashboardPage />);
    expect(screen.getByText('대시보드')).toBeInTheDocument();
  });

  it('renders summary cards', () => {
    vi.spyOn(useDashboardModule, 'useDashboard').mockReturnValue({
      data: MOCK_DASHBOARD,
      loading: false,
      error: null,
      refetch: vi.fn(),
    });
    render(<DashboardPage />);
    expect(screen.getByText('40')).toBeInTheDocument();
    expect(screen.getByText('전체 이슈')).toBeInTheDocument();
    expect(screen.getByText('완료 이슈')).toBeInTheDocument();
  });

  it('renders completion chart and agent stats', () => {
    vi.spyOn(useDashboardModule, 'useDashboard').mockReturnValue({
      data: MOCK_DASHBOARD,
      loading: false,
      error: null,
      refetch: vi.fn(),
    });
    render(<DashboardPage />);
    expect(screen.getByText('완료율')).toBeInTheDocument();
    expect(screen.getByText('에이전트별 이슈 현황')).toBeInTheDocument();
  });

  it('renders agent stats cards', () => {
    vi.spyOn(useDashboardModule, 'useDashboard').mockReturnValue({
      data: MOCK_DASHBOARD,
      loading: false,
      error: null,
      refetch: vi.fn(),
    });
    render(<DashboardPage />);
    expect(screen.getByText('agent-backend')).toBeInTheDocument();
  });

  it('shows retry button on error', () => {
    const refetch = vi.fn();
    vi.spyOn(useDashboardModule, 'useDashboard').mockReturnValue({
      data: null,
      loading: false,
      error: 'Failed',
      refetch,
    });
    render(<DashboardPage />);
    const retryButton = screen.getByText('재시도');
    expect(retryButton).toBeInTheDocument();
    retryButton.click();
    expect(refetch).toHaveBeenCalledOnce();
  });
});
