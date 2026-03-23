import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { IssueFormModal } from '../../components/IssueFormModal';

describe('IssueFormModal', () => {
  const defaultProps = {
    isOpen: true,
    onClose: jest.fn(),
    onSubmit: jest.fn(),
    availableLabels: ['frontend', 'backend'],
  };

  beforeEach(() => jest.clearAllMocks());

  test('renders nothing when closed', () => {
    render(<IssueFormModal {...defaultProps} isOpen={false} />);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  test('renders modal with form when open', () => {
    render(<IssueFormModal {...defaultProps} />);
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
  });

  test('shows Create Issue title for new issue', () => {
    render(<IssueFormModal {...defaultProps} />);
    expect(screen.getByText(/create issue/i)).toBeInTheDocument();
  });

  test('shows Edit Issue title when editing', () => {
    render(
      <IssueFormModal
        {...defaultProps}
        initialData={{
          id: '1',
          title: 'X',
          description: '',
          issue_type: 'task' as any,
          priority: 'medium' as any,
          labels: [],
          status: 'backlog' as any,
          created_at: '',
          updated_at: '',
        }}
      />
    );
    expect(screen.getByText(/edit issue/i)).toBeInTheDocument();
  });

  test('calls onClose when backdrop clicked', () => {
    render(<IssueFormModal {...defaultProps} />);
    fireEvent.click(screen.getByTestId('modal-backdrop'));
    expect(defaultProps.onClose).toHaveBeenCalled();
  });

  test('calls onClose on Escape key', () => {
    render(<IssueFormModal {...defaultProps} />);
    fireEvent.keyDown(screen.getByRole('dialog'), { key: 'Escape' });
    expect(defaultProps.onClose).toHaveBeenCalled();
  });
});
