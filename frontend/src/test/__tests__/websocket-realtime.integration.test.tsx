import { render, screen, act, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MockWebSocket } from '../setup';
import { Dashboard } from '../../components/Dashboard';
import { IssueStatus, IssuePriority, IssueType } from '../../types/issue';
import type { DashboardStats, WsEvent, Issue } from '../../types/issue';

const MOCK_STATS: DashboardStats = {
  status_counts: {
    [IssueStatus.BACKLOG]: 5,
    [IssueStatus.TODO]: 3,
    [IssueStatus.IN_PROGRESS]: 2,
    [IssueStatus.IN_REVIEW]: 1,
    [IssueStatus.DONE]: 8,
    [IssueStatus.CANCELLED]: 0,
  },
  priority_counts: {
    [IssuePriority.CRITICAL]: 1,
    [IssuePriority.HIGH]: 4,
    [IssuePriority.MEDIUM]: 7,
    [IssuePriority.LOW]: 7,
  },
  daily_created: [{ date: '2026-03-22', count: 3 }],
  daily_resolved: [{ date: '2026-03-22', count: 2 }],
};

const MOCK_ISSUE: Issue = {
  id: 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
  title: 'New test issue',
  issue_type: IssueType.TASK,
  status: IssueStatus.BACKLOG,
  priority: IssuePriority.HIGH,
  labels: [],
  created_at: '2026-03-23T00:00:00Z',
  updated_at: '2026-03-23T00:00:00Z',
};

function mockFetchSuccess(data: unknown): void {
  global.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: () => Promise.resolve(data),
  });
}

beforeEach(() => {
  MockWebSocket.reset();
  vi.useFakeTimers({ shouldAdvanceTime: true });
});

afterEach(() => {
  vi.useRealTimers();
  vi.restoreAllMocks();
});

describe('WebSocket Real-time Integration', () => {
  it('connects to WebSocket and shows live status', async () => {
    mockFetchSuccess(MOCK_STATS);
    render(<Dashboard />);

    await waitFor(() => expect(screen.getByTestId('dashboard')).toBeInTheDocument());

    const ws = MockWebSocket.latest()!;
    expect(ws).toBeDefined();
    expect(ws.url).toContain('/ws');

    act(() => ws.simulateOpen());
    expect(screen.getByTestId('ws-status')).toHaveTextContent('Live');
  });

  it('updates status counts on issue_created event', async () => {
    mockFetchSuccess(MOCK_STATS);
    render(<Dashboard />);

    await waitFor(() => expect(screen.getByTestId('dashboard')).toBeInTheDocument());

    const ws = MockWebSocket.latest()!;
    act(() => ws.simulateOpen());

    expect(screen.getByTestId('count-backlog')).toHaveTextContent('5');

    const event: WsEvent = {
      type: 'issue_created',
      payload: MOCK_ISSUE,
      timestamp: '2026-03-23T00:00:01Z',
    };
    act(() => ws.simulateMessage(event));

    expect(screen.getByTestId('count-backlog')).toHaveTextContent('6');
  });

  it('updates status counts on issue_status_changed event', async () => {
    mockFetchSuccess(MOCK_STATS);
    render(<Dashboard />);

    await waitFor(() => expect(screen.getByTestId('dashboard')).toBeInTheDocument());

    const ws = MockWebSocket.latest()!;
    act(() => ws.simulateOpen());

    const changedIssue: Issue = { ...MOCK_ISSUE, status: IssueStatus.IN_PROGRESS };
    const event: WsEvent = {
      type: 'issue_status_changed',
      payload: changedIssue,
      timestamp: '2026-03-23T00:00:02Z',
    };
    act(() => ws.simulateMessage(event));

    expect(screen.getByTestId('count-in_progress')).toHaveTextContent('3');
  });

  it('shows disconnected status on WebSocket close', async () => {
    mockFetchSuccess(MOCK_STATS);
    render(<Dashboard />);

    await waitFor(() => expect(screen.getByTestId('dashboard')).toBeInTheDocument());

    const ws = MockWebSocket.latest()!;
    act(() => ws.simulateOpen());
    expect(screen.getByTestId('ws-status')).toHaveTextContent('Live');

    act(() => ws.simulateClose());
    expect(screen.getByTestId('ws-status')).toHaveTextContent('Offline');
  });

  it('shows error status on WebSocket error', async () => {
    mockFetchSuccess(MOCK_STATS);
    render(<Dashboard />);

    await waitFor(() => expect(screen.getByTestId('dashboard')).toBeInTheDocument());

    const ws = MockWebSocket.latest()!;
    act(() => ws.simulateError());

    expect(screen.getByTestId('ws-status')).toHaveTextContent('Connection Error');
  });

  it('attempts reconnection after close', async () => {
    mockFetchSuccess(MOCK_STATS);
    render(<Dashboard />);

    await waitFor(() => expect(screen.getByTestId('dashboard')).toBeInTheDocument());

    const ws1 = MockWebSocket.latest()!;
    act(() => ws1.simulateOpen());
    act(() => ws1.simulateClose());

    const instancesBefore = MockWebSocket.instances.length;

    await act(async () => {
      vi.advanceTimersByTime(3000);
    });

    expect(MockWebSocket.instances.length).toBeGreaterThan(instancesBefore);
  });

  it('handles multiple rapid WebSocket events', async () => {
    mockFetchSuccess(MOCK_STATS);
    render(<Dashboard />);

    await waitFor(() => expect(screen.getByTestId('dashboard')).toBeInTheDocument());

    const ws = MockWebSocket.latest()!;
    act(() => ws.simulateOpen());

    const events: WsEvent[] = [
      { type: 'issue_created', payload: { ...MOCK_ISSUE, id: '11111111-1111-1111-1111-111111111111' }, timestamp: '2026-03-23T00:00:01Z' },
      { type: 'issue_created', payload: { ...MOCK_ISSUE, id: '22222222-2222-2222-2222-222222222222' }, timestamp: '2026-03-23T00:00:02Z' },
      { type: 'issue_created', payload: { ...MOCK_ISSUE, id: '33333333-3333-3333-3333-333333333333' }, timestamp: '2026-03-23T00:00:03Z' },
    ];

    act(() => {
      events.forEach((e) => ws.simulateMessage(e));
    });

    expect(screen.getByTestId('count-backlog')).toHaveTextContent('8');
  });

  it('ignores malformed WebSocket messages without crashing', async () => {
    mockFetchSuccess(MOCK_STATS);
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    render(<Dashboard />);

    await waitFor(() => expect(screen.getByTestId('dashboard')).toBeInTheDocument());

    const ws = MockWebSocket.latest()!;
    act(() => ws.simulateOpen());

    act(() => {
      ws.onmessage?.(new MessageEvent('message', { data: 'not-json' }));
    });

    expect(screen.getByTestId('dashboard')).toBeInTheDocument();
    consoleSpy.mockRestore();
  });
});
