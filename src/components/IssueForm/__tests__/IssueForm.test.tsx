import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { IssueForm } from '../IssueForm';
import { createMockIssue } from '@/test/fixtures';
import { ISSUE_STATUS, ISSUE_PRIORITY } from '@/types/issue';

describe('IssueForm', () => {
  const defaultProps = {
    onSubmit: vi.fn(),
    onCancel: vi.fn(),
  };

  it('renders empty form for new issue', () => {
    render(<IssueForm {...defaultProps} />);
    expect(screen.getByLabelText('Title')).toHaveValue('');
    expect(screen.getByLabelText('Description')).toHaveValue('');
  });

  it('renders pre-filled form when editing', () => {
    const issue = createMockIssue({ title: 'Edit me', description: 'Desc' });
    render(<IssueForm {...defaultProps} issue={issue} />);
    expect(screen.getByLabelText('Title')).toHaveValue('Edit me');
    expect(screen.getByLabelText('Description')).toHaveValue('Desc');
  });

  it('renders status select with all options', () => {
    render(<IssueForm {...defaultProps} />);
    const select = screen.getByLabelText('Status');
    expect(select).toBeInTheDocument();
    expect(screen.getByText('To Do')).toBeInTheDocument();
    expect(screen.getByText('In Progress')).toBeInTheDocument();
    expect(screen.getByText('Done')).toBeInTheDocument();
  });

  it('renders priority select with all options', () => {
    render(<IssueForm {...defaultProps} />);
    const select = screen.getByLabelText('Priority');
    expect(select).toBeInTheDocument();
    expect(screen.getByText('Low')).toBeInTheDocument();
    expect(screen.getByText('High')).toBeInTheDocument();
    expect(screen.getByText('Urgent')).toBeInTheDocument();
  });

  it('defaults status to backlog and priority to medium', () => {
    render(<IssueForm {...defaultProps} />);
    expect(screen.getByLabelText('Status')).toHaveValue(ISSUE_STATUS.BACKLOG);
    expect(screen.getByLabelText('Priority')).toHaveValue(ISSUE_PRIORITY.MEDIUM);
  });

  it('calls onSubmit with form data', async () => {
    const user = userEvent.setup();
    render(<IssueForm {...defaultProps} />);
    await user.type(screen.getByLabelText('Title'), 'New issue');
    await user.type(screen.getByLabelText('Description'), 'Some description');
    await user.click(screen.getByTestId('submit-button'));
    expect(defaultProps.onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'New issue',
        description: 'Some description',
        status: ISSUE_STATUS.BACKLOG,
        priority: ISSUE_PRIORITY.MEDIUM,
      })
    );
  });

  it('prevents submit when title is empty', async () => {
    const user = userEvent.setup();
    render(<IssueForm {...defaultProps} />);
    await user.click(screen.getByTestId('submit-button'));
    expect(defaultProps.onSubmit).not.toHaveBeenCalled();
    expect(screen.getByText('Title is required')).toBeInTheDocument();
  });

  it('calls onCancel when cancel button is clicked', async () => {
    const user = userEvent.setup();
    render(<IssueForm {...defaultProps} />);
    await user.click(screen.getByTestId('cancel-button'));
    expect(defaultProps.onCancel).toHaveBeenCalledTimes(1);
  });

  it('shows validation error for whitespace-only title', async () => {
    const user = userEvent.setup();
    render(<IssueForm {...defaultProps} />);
    await user.type(screen.getByLabelText('Title'), '   ');
    await user.click(screen.getByTestId('submit-button'));
    expect(defaultProps.onSubmit).not.toHaveBeenCalled();
    expect(screen.getByText('Title is required')).toBeInTheDocument();
  });

  it('clears validation error when user starts typing', async () => {
    const user = userEvent.setup();
    render(<IssueForm {...defaultProps} />);
    await user.click(screen.getByTestId('submit-button'));
    expect(screen.getByText('Title is required')).toBeInTheDocument();
    await user.type(screen.getByLabelText('Title'), 'a');
    expect(screen.queryByText('Title is required')).not.toBeInTheDocument();
  });

  it('renders assignee input field', () => {
    render(<IssueForm {...defaultProps} />);
    expect(screen.getByLabelText('Assignee')).toBeInTheDocument();
  });

  it('submits with changed status and priority', async () => {
    const user = userEvent.setup();
    render(<IssueForm {...defaultProps} />);
    await user.type(screen.getByLabelText('Title'), 'Urgent task');
    await user.selectOptions(screen.getByLabelText('Status'), ISSUE_STATUS.TODO);
    await user.selectOptions(screen.getByLabelText('Priority'), ISSUE_PRIORITY.URGENT);
    await user.click(screen.getByTestId('submit-button'));
    expect(defaultProps.onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Urgent task',
        status: ISSUE_STATUS.TODO,
        priority: ISSUE_PRIORITY.URGENT,
      })
    );
  });

  it('shows Save label for edit mode, Create for new', () => {
    const { rerender } = render(<IssueForm {...defaultProps} />);
    expect(screen.getByTestId('submit-button')).toHaveTextContent('Create');
    const issue = createMockIssue();
    rerender(<IssueForm {...defaultProps} issue={issue} />);
    expect(screen.getByTestId('submit-button')).toHaveTextContent('Save');
  });
});