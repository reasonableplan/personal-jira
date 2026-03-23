import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { SidePanel } from '../SidePanel';
import { createMockIssue } from '@/test/fixtures';
import { ISSUE_STATUS, ISSUE_PRIORITY } from '@/types/issue';

describe('SidePanel', () => {
  const mockIssue = createMockIssue({
    title: 'Panel test issue',
    description: 'Detailed description here',
    status: ISSUE_STATUS.IN_PROGRESS,
    priority: ISSUE_PRIORITY.HIGH,
    assignee: 'alice',
  });

  const defaultProps = {
    issue: mockIssue,
    open: true,
    onClose: vi.fn(),
    onEdit: vi.fn(),
    onDelete: vi.fn(),
  };

  it('renders issue title', () => {
    render(<SidePanel {...defaultProps} />);
    expect(screen.getByText('Panel test issue')).toBeInTheDocument();
  });

  it('renders issue description', () => {
    render(<SidePanel {...defaultProps} />);
    expect(screen.getByText('Detailed description here')).toBeInTheDocument();
  });

  it('renders status and priority fields', () => {
    render(<SidePanel {...defaultProps} />);
    expect(screen.getByText('In Progress')).toBeInTheDocument();
    expect(screen.getByText('High')).toBeInTheDocument();
  });

  it('renders assignee', () => {
    render(<SidePanel {...defaultProps} />);
    expect(screen.getByText('alice')).toBeInTheDocument();
  });

  it('shows unassigned text when assignee is null', () => {
    const unassigned = createMockIssue({ assignee: null });
    render(<SidePanel {...defaultProps} issue={unassigned} />);
    expect(screen.getByText('Unassigned')).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', async () => {
    const user = userEvent.setup();
    render(<SidePanel {...defaultProps} />);
    await user.click(screen.getByTestId('close-button'));
    expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
  });

  it('calls onEdit when edit button is clicked', async () => {
    const user = userEvent.setup();
    render(<SidePanel {...defaultProps} />);
    await user.click(screen.getByTestId('edit-button'));
    expect(defaultProps.onEdit).toHaveBeenCalledWith(mockIssue);
  });

  it('calls onDelete when delete button is clicked', async () => {
    const user = userEvent.setup();
    render(<SidePanel {...defaultProps} />);
    await user.click(screen.getByTestId('delete-button'));
    expect(defaultProps.onDelete).toHaveBeenCalledWith(mockIssue.id);
  });

  it('does not render when open is false', () => {
    render(<SidePanel {...defaultProps} open={false} />);
    expect(screen.queryByText('Panel test issue')).not.toBeInTheDocument();
  });

  it('renders with null issue gracefully', () => {
    render(<SidePanel {...defaultProps} issue={null} />);
    expect(screen.getByText('No issue selected')).toBeInTheDocument();
  });

  it('displays created and updated timestamps', () => {
    render(<SidePanel {...defaultProps} />);
    expect(screen.getByTestId('created-at')).toBeInTheDocument();
    expect(screen.getByTestId('updated-at')).toBeInTheDocument();
  });

  it('has correct aria role for accessibility', () => {
    render(<SidePanel {...defaultProps} />);
    expect(screen.getByRole('complementary')).toBeInTheDocument();
  });
});