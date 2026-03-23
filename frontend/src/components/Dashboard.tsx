import React from 'react';
import type { DashboardStats } from '../types/issue';
import { IssueStatus, IssuePriority } from '../types/issue';
import { useDashboard, applyWsEventToStats } from '../hooks/useDashboard';
import { useWebSocket } from '../hooks/useWebSocket';
import type { ConnectionStatus } from '../hooks/useWebSocket';
import type { WsEvent } from '../types/issue';

const WS_URL = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000/ws';

const STATUS_LABELS: Record<IssueStatus, string> = {
  [IssueStatus.BACKLOG]: 'Backlog',
  [IssueStatus.TODO]: 'To Do',
  [IssueStatus.IN_PROGRESS]: 'In Progress',
  [IssueStatus.IN_REVIEW]: 'In Review',
  [IssueStatus.DONE]: 'Done',
  [IssueStatus.CANCELLED]: 'Cancelled',
};

const PRIORITY_LABELS: Record<IssuePriority, string> = {
  [IssuePriority.CRITICAL]: 'Critical',
  [IssuePriority.HIGH]: 'High',
  [IssuePriority.MEDIUM]: 'Medium',
  [IssuePriority.LOW]: 'Low',
};

const CONNECTION_STATUS_TEXT: Record<ConnectionStatus, string> = {
  connecting: 'Connecting...',
  connected: 'Live',
  disconnected: 'Offline',
  error: 'Connection Error',
};

interface StatusBarChartProps {
  data: DashboardStats['status_counts'];
}

export const StatusBarChart: React.FC<StatusBarChartProps> = ({ data }) => {
  const maxCount = Math.max(...Object.values(data), 1);
  return (
    <div data-testid="status-bar-chart" role="figure" aria-label="Issues by Status">
      {Object.entries(STATUS_LABELS).map(([status, label]) => {
        const count = data[status as IssueStatus] ?? 0;
        const width = `${(count / maxCount) * 100}%`;
        return (
          <div key={status} className="chart-bar-row">
            <span className="chart-label">{label}</span>
            <div className="chart-bar-track">
              <div
                className="chart-bar-fill"
                style={{ width }}
                data-testid={`bar-${status}`}
                role="meter"
                aria-valuenow={count}
                aria-valuemin={0}
                aria-valuemax={maxCount}
                aria-label={`${label}: ${count}`}
              />
            </div>
            <span className="chart-count" data-testid={`count-${status}`}>{count}</span>
          </div>
        );
      })}
    </div>
  );
};

interface PrioritySummaryProps {
  data: DashboardStats['priority_counts'];
}

export const PrioritySummary: React.FC<PrioritySummaryProps> = ({ data }) => (
  <ul data-testid="priority-summary" aria-label="Issues by Priority">
    {Object.entries(PRIORITY_LABELS).map(([priority, label]) => {
      const count = data[priority as IssuePriority] ?? 0;
      return (
        <li key={priority} data-testid={`priority-${priority}`}>
          {label}: {count}
        </li>
      );
    })}
  </ul>
);

export const Dashboard: React.FC = () => {
  const { stats, loading, error, refresh } = useDashboard();
  const [liveStats, setLiveStats] = React.useState<DashboardStats | null>(null);

  React.useEffect(() => {
    setLiveStats(stats);
  }, [stats]);

  const handleWsMessage = React.useCallback((event: WsEvent) => {
    setLiveStats((prev) => (prev ? applyWsEventToStats(prev, event) : prev));
  }, []);

  const { status: wsStatus } = useWebSocket({
    url: WS_URL,
    onMessage: handleWsMessage,
  });

  if (loading) return <div data-testid="dashboard-loading">Loading dashboard...</div>;
  if (error) return <div data-testid="dashboard-error" role="alert">{error}</div>;
  if (!liveStats) return null;

  return (
    <div data-testid="dashboard">
      <header>
        <h1>Dashboard</h1>
        <span data-testid="ws-status" className={`ws-status ws-status--${wsStatus}`}>
          {CONNECTION_STATUS_TEXT[wsStatus]}
        </span>
        <button onClick={refresh} data-testid="refresh-btn">Refresh</button>
      </header>
      <section aria-label="Status Distribution">
        <h2>Issues by Status</h2>
        <StatusBarChart data={liveStats.status_counts} />
      </section>
      <section aria-label="Priority Distribution">
        <h2>Issues by Priority</h2>
        <PrioritySummary data={liveStats.priority_counts} />
      </section>
    </div>
  );
};
