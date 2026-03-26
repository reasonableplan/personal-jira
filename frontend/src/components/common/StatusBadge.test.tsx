import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { StatusBadge } from './StatusBadge';
import type { TaskStatus } from '@/types/task';
import { TASK_STATUS } from '@/types/task';

describe('StatusBadge', () => {
  const cases: Array<{ status: TaskStatus; label: string }> = [
    { status: TASK_STATUS.TODO, label: 'To Do' },
    { status: TASK_STATUS.IN_PROGRESS, label: 'In Progress' },
    { status: TASK_STATUS.IN_REVIEW, label: 'In Review' },
    { status: TASK_STATUS.DONE, label: 'Done' },
  ];

  cases.forEach(({ status, label }) => {
    it(`renders "${label}" for status "${status}"`, () => {
      render(<StatusBadge status={status} />);
      expect(screen.getByText(label)).toBeInTheDocument();
    });
  });

  it('applies custom className', () => {
    const { container } = render(
      <StatusBadge status={TASK_STATUS.TODO} className="custom-class" />,
    );
    expect(container.firstChild).toHaveClass('custom-class');
  });
});
