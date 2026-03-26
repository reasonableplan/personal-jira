import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { EmptyState } from './EmptyState';

describe('EmptyState', () => {
  it('renders title', () => {
    render(<EmptyState title="No tasks found" />);
    expect(screen.getByText('No tasks found')).toBeInTheDocument();
  });

  it('renders description when provided', () => {
    render(
      <EmptyState
        title="No tasks found"
        description="Create your first task to get started."
      />,
    );
    expect(
      screen.getByText('Create your first task to get started.'),
    ).toBeInTheDocument();
  });

  it('does not render description when not provided', () => {
    const { container } = render(<EmptyState title="No tasks found" />);
    expect(container.querySelectorAll('p')).toHaveLength(0);
  });

  it('renders action when provided', () => {
    render(
      <EmptyState
        title="No tasks found"
        action={<button>Create task</button>}
      />,
    );
    expect(screen.getByText('Create task')).toBeInTheDocument();
  });

  it('renders custom icon when provided', () => {
    render(
      <EmptyState
        title="No tasks found"
        icon={<span data-testid="custom-icon">icon</span>}
      />,
    );
    expect(screen.getByTestId('custom-icon')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <EmptyState title="No tasks found" className="custom-class" />,
    );
    expect(container.firstChild).toHaveClass('custom-class');
  });
});
