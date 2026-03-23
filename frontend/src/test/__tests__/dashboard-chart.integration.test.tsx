import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MockWebSocket } from '../setup';
import { Dashboard, StatusBarChart, PrioritySummary } from '../../components/Dashboard';
import { IssueStatus, IssuePriority } from '../../types/issue';
import type { DashboardStats } from '../../types/issue';

const MOCK_STATS: DashboardStats = {
  status_counts: {
    [IssueStatus.BACKLOG]: 10,
    [IssueStatus.TODO]: 5,
    [IssueStatus.IN_PROGRESS]: 3,
    [IssueStatus.IN_REVIEW]: 2,
    [IssueStatus.DONE]: 15,
    [IssueStatus.CANCELLED]: 1,
  },
  priority_counts: {
    [IssuePriority.CRITICAL]: 2,
    [IssuePriority.HIGH]: 8,
    [IssuePriority.MEDIUM]: 12,
    [IssuePriority.LOW]: 14,
  },
  daily_created: [
    { date: '2026-03-20', count: 5 },
    { date: '2026-03-21', count: 3 },
    { date: '2026-03-22', count: 7 },
  ],
  daily_resolved: [
    { date: '2026-03-20', count: 2 },
    { date: '2026-03-21', count: 4 },
    { date: '2026-03-22', count: 6 },
  ],
};

function mockFetchSuccess(data: unknown): void {
  global.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: () => Promise.resolve(data),
  });
}

function mockFetchError(status: number, statusText: string): void {
  global.fetch = vi.fn().mockResolvedValue({
    ok: false,
    status,
    statusText,
  });
}

function mockFetchNetworkError(): void {
  global.fetch = vi.fn().mockRejectedValue(new TypeError('Failed to fetch'));
}

beforeEach(() => {
  MockWebSocket.reset();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('Dashboard Chart Data Loading Integration', () => {
  it('shows loading state initially', () => {
    global.fetch = vi.fn().mockReturnValue(new Promise(() => {}));
    render(<Dashboard />);
    expect(screen.getByTestId('dashboard-loading')).toHaveTextContent('Loading dashboard...');
  });

  it('renders status bar chart with fetched data', async () => {
    mockFetchSuccess(MOCK_STATS);
    render(<Dashboard />);

    await waitFor(() => expect(screen.getByTestId('status-bar-chart')).toBeInTheDocument());

    expect(screen.getByTestId('count-backlog')).toHaveTextContent('10');
    expect(screen.getByTestId('count-todo')).toHaveTextContent('5');
    expect(screen.getByTestId('count-in_progress')).toHaveTextContent('3');
    expect(screen.getByTestId('count-in_review')).toHaveTextContent('2');
    expect(screen.getByTestId('count-done')).toHaveTextContent('15');
    expect(screen.getByTestId('count-cancelled')).toHaveTextContent('1');
  });

  it('renders priority summary with fetched data', async () => {
    mockFetchSuccess(MOCK_STATS);
    render(<Dashboard />);

    await waitFor(() => expect(screen.getByTestId('priority-summary')).toBeInTheDocument());

    expect(screen.getByTestId('priority-critical')).toHaveTextContent('Critical: 2');
    expect(screen.getByTestId('priority-high')).toHaveTextContent('High: 8');
    expect(screen.getByTestId('priority-medium')).toHaveTextContent('Medium: 12');
    expect(screen.getByTestId('priority-low')).toHaveTextContent('Low: 14');
  });

  it('shows error message on API failure', async () => {
    mockFetchError(500, 'Internal Server Error');
    render(<Dashboard />);

    await waitFor(() => expect(screen.getByTestId('dashboard-error')).toBeInTheDocument());
    expect(screen.getByTestId('dashboard-error')).toHaveTextContent('API error: 500 Internal Server Error');
  });

  it('shows error message on network failure', async () => {
    mockFetchNetworkError();
    render(<Dashboard />);

    await waitFor(() => expect(screen.getByTestId('dashboard-error')).toBeInTheDocument());
    expect(screen.getByTestId('dashboard-error')).toHaveTextContent('Failed to fetch');
  });

  it('refreshes data on button click', async () => {
    const user = userEvent.setup();
    mockFetchSuccess(MOCK_STATS);
    render(<Dashboard />);

    await waitFor(() => expect(screen.getByTestId('dashboard')).toBeInTheDocument());
    expect(global.fetch).toHaveBeenCalledTimes(1);

    const updatedStats: DashboardStats = {
      ...MOCK_STATS,
      status_counts: { ...MOCK_STATS.status_counts, [IssueStatus.DONE]: 20 },
    };
    mockFetchSuccess(updatedStats);

    await user.click(screen.getByTestId('refresh-btn'));

    await waitFor(() => expect(screen.getByTestId('count-done')).toHaveTextContent('20'));
  });

  it('calls correct API endpoint', async () => {
    mockFetchSuccess(MOCK_STATS);
    render(<Dashboard />);

    await waitFor(() => expect(screen.getByTestId('dashboard')).toBeInTheDocument());

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/dashboard/stats'),
      expect.objectContaining({ headers: { 'Content-Type': 'application/json' } }),
    );
  });

  it('status bar chart has correct ARIA attributes', async () => {
    mockFetchSuccess(MOCK_STATS);
    render(<Dashboard />);

    await waitFor(() => expect(screen.getByTestId('status-bar-chart')).toBeInTheDocument());

    const chart = screen.getByTestId('status-bar-chart');
    expect(chart).toHaveAttribute('aria-label', 'Issues by Status');

    const doneBar = screen.getByTestId('bar-done');
    expect(doneBar).toHaveAttribute('role', 'meter');
    expect(doneBar).toHaveAttribute('aria-valuenow', '15');
    expect(doneBar).toHaveAttribute('aria-valuemin', '0');
  });

  it('priority summary has correct ARIA attributes', async () => {
    mockFetchSuccess(MOCK_STATS);
    render(<Dashboard />);

    await waitFor(() => expect(screen.getByTestId('priority-summary')).toBeInTheDocument());

    const summary = screen.getByTestId('priority-summary');
    expect(summary).toHaveAttribute('aria-label', 'Issues by Priority');
  });
});

describe('StatusBarChart unit', () => {
  it('renders all status bars', () => {
    render(<StatusBarChart data={MOCK_STATS.status_counts} />);
    expect(screen.getByTestId('bar-backlog')).toBeInTheDocument();
    expect(screen.getByTestId('bar-done')).toBeInTheDocument();
    expect(screen.getByTestId('bar-cancelled')).toBeInTheDocument();
  });

  it('normalizes bar widths relative to max count', () => {
    render(<StatusBarChart data={MOCK_STATS.status_counts} />);
    const doneBar = screen.getByTestId('bar-done');
    expect(doneBar.style.width).toBe('100%');

    const cancelledBar = screen.getByTestId('bar-cancelled');
    const expectedWidth = `${(1 / 15) * 100}%`;
    expect(cancelledBar.style.width).toBe(expectedWidth);
  });

  it('handles all-zero counts without division error', () => {
    const zeroCounts = {
      [IssueStatus.BACKLOG]: 0,
      [IssueStatus.TODO]: 0,
      [IssueStatus.IN_PROGRESS]: 0,
      [IssueStatus.IN_REVIEW]: 0,
      [IssueStatus.DONE]: 0,
      [IssueStatus.CANCELLED]: 0,
    };
    render(<StatusBarChart data={zeroCounts} />);
    expect(screen.getByTestId('bar-backlog').style.width).toBe('0%');
  });
});

describe('PrioritySummary unit', () => {
  it('renders all priority items', () => {
    render(<PrioritySummary data={MOCK_STATS.priority_counts} />);
    expect(screen.getByTestId('priority-critical')).toBeInTheDocument();
    expect(screen.getByTestId('priority-high')).toBeInTheDocument();
    expect(screen.getByTestId('priority-medium')).toBeInTheDocument();
    expect(screen.getByTestId('priority-low')).toBeInTheDocument();
  });

  it('displays count values correctly', () => {
    render(<PrioritySummary data={MOCK_STATS.priority_counts} />);
    expect(screen.getByTestId('priority-critical')).toHaveTextContent('Critical: 2');
    expect(screen.getByTestId('priority-low')).toHaveTextContent('Low: 14');
  });
});
