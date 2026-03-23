import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { IssueForm } from '../../components/IssueForm';
import { IssueType, IssuePriority, IssueStatus } from '../../types/issue';
import type { Issue, IssueFormData } from '../../types/issue';

const AVAILABLE_LABELS = ['frontend', 'backend', 'bug'];

describe('IssueForm', () => {
  const defaultProps = {
    onSubmit: jest.fn(),
    onCancel: jest.fn(),
    availableLabels: AVAILABLE_LABELS,
  };

  beforeEach(() => jest.clearAllMocks());

  test('renders empty form in create mode', () => {
    render(<IssueForm {...defaultProps} />);
    expect(screen.getByLabelText(/title/i)).toHaveValue('');
    expect(screen.getByLabelText(/type/i)).toHaveValue(IssueType.TASK);
    expect(screen.getByLabelText(/priority/i)).toHaveValue(IssuePriority.MEDIUM);
  });

  test('renders pre-filled form in edit mode', () => {
    const issue: Issue = {
      id: '1',
      title: 'Fix login',
      description: '**broken**',
      issue_type: IssueType.BUG,
      priority: IssuePriority.HIGH,
      labels: ['frontend'],
      status: IssueStatus.IN_PROGRESS,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    };
    render(<IssueForm {...defaultProps} initialData={issue} />);
    expect(screen.getByLabelText(/title/i)).toHaveValue('Fix login');
    expect(screen.getByLabelText(/type/i)).toHaveValue(IssueType.BUG);
    expect(screen.getByLabelText(/priority/i)).toHaveValue(IssuePriority.HIGH);
  });

  test('submit button shows Create for new issue', () => {
    render(<IssueForm {...defaultProps} />);
    expect(screen.getByRole('button', { name: /create/i })).toBeInTheDocument();
  });

  test('submit button shows Save for edit mode', () => {
    const issue: Issue = {
      id: '1',
      title: 'X',
      description: '',
      issue_type: IssueType.TASK,
      priority: IssuePriority.LOW,
      labels: [],
      status: IssueStatus.BACKLOG,
      created_at: '',
      updated_at: '',
    };
    render(<IssueForm {...defaultProps} initialData={issue} />);
    expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
  });

  test('validates title is required', async () => {
    render(<IssueForm {...defaultProps} />);
    fireEvent.click(screen.getByRole('button', { name: /create/i }));
    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
    });
    expect(defaultProps.onSubmit).not.toHaveBeenCalled();
  });

  test('validates title max length', async () => {
    render(<IssueForm {...defaultProps} />);
    const titleInput = screen.getByLabelText(/title/i);
    fireEvent.change(titleInput, { target: { value: 'a'.repeat(201) } });
    fireEvent.click(screen.getByRole('button', { name: /create/i }));
    await waitFor(() => {
      expect(screen.getByText(/200 characters/i)).toBeInTheDocument();
    });
  });

  test('calls onSubmit with form data', async () => {
    render(<IssueForm {...defaultProps} />);
    fireEvent.change(screen.getByLabelText(/title/i), {
      target: { value: 'New task' },
    });
    fireEvent.click(screen.getByRole('button', { name: /create/i }));
    await waitFor(() => {
      expect(defaultProps.onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'New task',
          issue_type: IssueType.TASK,
          priority: IssuePriority.MEDIUM,
        })
      );
    });
  });

  test('calls onCancel when cancel clicked', () => {
    render(<IssueForm {...defaultProps} />);
    fireEvent.click(screen.getByRole('button', { name: /cancel/i }));
    expect(defaultProps.onCancel).toHaveBeenCalled();
  });

  test('disables form when submitting', () => {
    render(<IssueForm {...defaultProps} isSubmitting />);
    expect(screen.getByLabelText(/title/i)).toBeDisabled();
    expect(screen.getByRole('button', { name: /create|save/i })).toBeDisabled();
  });

  test('shows server error', () => {
    render(<IssueForm {...defaultProps} serverError="Network error" />);
    expect(screen.getByRole('alert')).toHaveTextContent('Network error');
  });
});
