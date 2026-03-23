import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { TableView } from '../TableView';
import { MOCK_ISSUES } from '@/test/fixtures';

const EXPECTED_HEADERS = ['Title', 'Status', 'Priority', 'Assignee'];

describe('TableView', () => {
  const defaultProps = {
    issues: MOCK_ISSUES,
    onIssueClick: vi.fn(),
    onSort: vi.fn(),
  };

  it('renders table headers', () => {
    render(<TableView {...defaultProps} />);
    for (const header of EXPECTED_HEADERS) {
      expect(screen.getByText(header)).toBeInTheDocument();
    }
  });

  it('renders all issues as rows', () => {
    render(<TableView {...defaultProps} />);
    const rows = screen.getAllByTestId('issue-row');
    expect(rows).toHaveLength(MOCK_ISSUES.length);
  });

  it('displays issue data in correct cells', () => {
    render(<TableView {...defaultProps} />);
    const firstRow = screen.getAllByTestId('issue-row')[0];
    expect(within(firstRow).getByText('Set up CI pipeline')).toBeInTheDocument();
    expect(within(firstRow).getByText('To Do')).toBeInTheDocument();
    expect(within(firstRow).getByText('High')).toBeInTheDocument();
    expect(within(firstRow).getByText('alice')).toBeInTheDocument();
  });

  it('shows dash for null assignee', () => {
    render(<TableView {...defaultProps} />);
    const backlogRow = screen.getAllByTestId('issue-row')[3];
    expect(within(backlogRow).getByTestId('assignee-cell')).toHaveTextContent('—');
  });

  it('calls onIssueClick when a row is clicked', async () => {
    const user = userEvent.setup();
    render(<TableView {...defaultProps} />);
    const firstRow = screen.getAllByTestId('issue-row')[0];
    await user.click(firstRow);
    expect(defaultProps.onIssueClick).toHaveBeenCalledWith(MOCK_ISSUES[0]);
  });

  it('calls onSort when a header is clicked', async () => {
    const user = userEvent.setup();
    render(<TableView {...defaultProps} />);
    await user.click(screen.getByText('Title'));
    expect(defaultProps.onSort).toHaveBeenCalledWith('title');
  });

  it('renders empty state when no issues', () => {
    render(<TableView {...defaultProps} issues={[]} />);
    expect(screen.getByText('No issues found')).toBeInTheDocument();
    expect(screen.queryAllByTestId('issue-row')).toHaveLength(0);
  });

  it('highlights row on hover via data attribute', () => {
    render(<TableView {...defaultProps} />);
    const rows = screen.getAllByTestId('issue-row');
    expect(rows[0]).toHaveAttribute('data-issue-id', MOCK_ISSUES[0].id);
  });

  it('renders sortable header indicators', () => {
    render(<TableView {...defaultProps} sortField="title" sortDirection="asc" />);
    const titleHeader = screen.getByTestId('sort-indicator-title');
    expect(titleHeader).toHaveTextContent('▲');
  });

  it('renders descending sort indicator', () => {
    render(<TableView {...defaultProps} sortField="priority" sortDirection="desc" />);
    const priorityHeader = screen.getByTestId('sort-indicator-priority');
    expect(priorityHeader).toHaveTextContent('▼');
  });
});