import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { IssueDetailPanel } from '../IssueDetailPanel';
import type { Issue } from '../../../types/issue';

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

describe('IssueDetailPanel', () => {
  const onClose = jest.fn();

  beforeEach(() => {
    onClose.mockClear();
  });

  it('renders nothing when closed', () => {
    const { container } = render(
      <IssueDetailPanel issue={null} open={false} onClose={onClose} />
    );
    expect(container.querySelector('[data-testid="issue-detail-panel"]')).not.toBeInTheDocument();
  });

  it('renders panel when open with issue', () => {
    render(<IssueDetailPanel issue={MOCK_ISSUE} open={true} onClose={onClose} />);
    expect(screen.getByTestId('issue-detail-panel')).toBeInTheDocument();
    expect(screen.getByText('Fix login redirect')).toBeInTheDocument();
  });

  it('displays issue metadata', () => {
    render(<IssueDetailPanel issue={MOCK_ISSUE} open={true} onClose={onClose} />);
    expect(screen.getByText('IN_PROGRESS')).toBeInTheDocument();
    expect(screen.getByText('HIGH')).toBeInTheDocument();
    expect(screen.getByText('BUG')).toBeInTheDocument();
  });

  it('calls onClose when close button clicked', () => {
    render(<IssueDetailPanel issue={MOCK_ISSUE} open={true} onClose={onClose} />);
    fireEvent.click(screen.getByLabelText('Close panel'));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when overlay clicked', () => {
    render(<IssueDetailPanel issue={MOCK_ISSUE} open={true} onClose={onClose} />);
    fireEvent.click(screen.getByTestId('panel-overlay'));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('shows detail tab by default', () => {
    render(<IssueDetailPanel issue={MOCK_ISSUE} open={true} onClose={onClose} />);
    expect(screen.getByRole('tab', { name: '상세' })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByText('Users are not redirected after login')).toBeInTheDocument();
  });

  it('switches to comments tab', () => {
    render(<IssueDetailPanel issue={MOCK_ISSUE} open={true} onClose={onClose} />);
    fireEvent.click(screen.getByRole('tab', { name: '코멘트' }));
    expect(screen.getByRole('tab', { name: '코멘트' })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByTestId('tab-content-comments')).toBeInTheDocument();
  });

  it('switches to logs tab', () => {
    render(<IssueDetailPanel issue={MOCK_ISSUE} open={true} onClose={onClose} />);
    fireEvent.click(screen.getByRole('tab', { name: '로그' }));
    expect(screen.getByRole('tab', { name: '로그' })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByTestId('tab-content-logs')).toBeInTheDocument();
  });

  it('switches to artifacts tab', () => {
    render(<IssueDetailPanel issue={MOCK_ISSUE} open={true} onClose={onClose} />);
    fireEvent.click(screen.getByRole('tab', { name: '아티팩트' }));
    expect(screen.getByRole('tab', { name: '아티팩트' })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByTestId('tab-content-artifacts')).toBeInTheDocument();
  });

  it('closes on Escape key', () => {
    render(<IssueDetailPanel issue={MOCK_ISSUE} open={true} onClose={onClose} />);
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('applies slide-in animation class when open', () => {
    render(<IssueDetailPanel issue={MOCK_ISSUE} open={true} onClose={onClose} />);
    const panel = screen.getByTestId('issue-detail-panel');
    expect(panel.className).toMatch(/slideIn/);
  });
});
