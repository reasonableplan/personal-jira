import { render, screen } from '@testing-library/react';
import { DetailTab } from '../tabs/DetailTab';
import { CommentsTab } from '../tabs/CommentsTab';
import { LogsTab } from '../tabs/LogsTab';
import { ArtifactsTab } from '../tabs/ArtifactsTab';
import type { Issue, Comment, ActivityLog, Artifact } from '../../../types/issue';

const MOCK_ISSUE: Issue = {
  id: 'issue-001',
  title: 'Fix login redirect',
  description: 'Users are not redirected after login',
  status: 'IN_PROGRESS',
  priority: 'HIGH',
  issue_type: 'BUG',
  assignee_id: 'agent-1',
  created_at: '2026-03-20T10:00:00Z',
  updated_at: '2026-03-22T14:30:00Z',
};

const MOCK_COMMENTS: Comment[] = [
  { id: 'c1', issue_id: 'issue-001', author: 'agent-1', content: 'Started investigation', created_at: '2026-03-21T09:00:00Z' },
  { id: 'c2', issue_id: 'issue-001', author: 'agent-2', content: 'Found root cause', created_at: '2026-03-21T10:00:00Z' },
];

const MOCK_LOGS: ActivityLog[] = [
  { id: 'l1', issue_id: 'issue-001', action: 'status_change', actor: 'agent-1', detail: 'TODO → IN_PROGRESS', created_at: '2026-03-21T08:00:00Z' },
];

const MOCK_ARTIFACTS: Artifact[] = [
  { id: 'a1', issue_id: 'issue-001', filename: 'error.log', url: '/files/error.log', size_bytes: 2048, uploaded_at: '2026-03-21T11:00:00Z' },
];

describe('DetailTab', () => {
  it('renders issue description', () => {
    render(<DetailTab issue={MOCK_ISSUE} />);
    expect(screen.getByText('Users are not redirected after login')).toBeInTheDocument();
  });

  it('renders status badge', () => {
    render(<DetailTab issue={MOCK_ISSUE} />);
    expect(screen.getByText('IN_PROGRESS')).toBeInTheDocument();
  });

  it('renders priority and type', () => {
    render(<DetailTab issue={MOCK_ISSUE} />);
    expect(screen.getByText('HIGH')).toBeInTheDocument();
    expect(screen.getByText('BUG')).toBeInTheDocument();
  });

  it('renders timestamps', () => {
    render(<DetailTab issue={MOCK_ISSUE} />);
    expect(screen.getByText(/2026-03-20/)).toBeInTheDocument();
    expect(screen.getByText(/2026-03-22/)).toBeInTheDocument();
  });
});

describe('CommentsTab', () => {
  it('renders comment list', () => {
    render(<CommentsTab comments={MOCK_COMMENTS} loading={false} />);
    expect(screen.getByText('Started investigation')).toBeInTheDocument();
    expect(screen.getByText('Found root cause')).toBeInTheDocument();
  });

  it('renders empty state', () => {
    render(<CommentsTab comments={[]} loading={false} />);
    expect(screen.getByText('코멘트가 없습니다')).toBeInTheDocument();
  });

  it('renders loading state', () => {
    render(<CommentsTab comments={[]} loading={true} />);
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });
});

describe('LogsTab', () => {
  it('renders activity logs', () => {
    render(<LogsTab logs={MOCK_LOGS} loading={false} />);
    expect(screen.getByText('status_change')).toBeInTheDocument();
    expect(screen.getByText('TODO → IN_PROGRESS')).toBeInTheDocument();
  });

  it('renders empty state', () => {
    render(<LogsTab logs={[]} loading={false} />);
    expect(screen.getByText('활동 로그가 없습니다')).toBeInTheDocument();
  });
});

describe('ArtifactsTab', () => {
  it('renders artifact list', () => {
    render(<ArtifactsTab artifacts={MOCK_ARTIFACTS} loading={false} />);
    expect(screen.getByText('error.log')).toBeInTheDocument();
    expect(screen.getByText('2.0 KB')).toBeInTheDocument();
  });

  it('renders empty state', () => {
    render(<ArtifactsTab artifacts={[]} loading={false} />);
    expect(screen.getByText('아티팩트가 없습니다')).toBeInTheDocument();
  });
});
