import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { PriorityBadge } from './PriorityBadge';
import type { Priority } from '@/types/priority';
import { PRIORITY } from '@/types/priority';

describe('PriorityBadge', () => {
  const cases: Array<{ priority: Priority; label: string }> = [
    { priority: PRIORITY.CRITICAL, label: 'Critical' },
    { priority: PRIORITY.HIGH, label: 'High' },
    { priority: PRIORITY.MEDIUM, label: 'Medium' },
    { priority: PRIORITY.LOW, label: 'Low' },
    { priority: PRIORITY.LOWEST, label: 'Lowest' },
  ];

  cases.forEach(({ priority, label }) => {
    it(`renders "${label}" for priority ${priority}`, () => {
      render(<PriorityBadge priority={priority} />);
      expect(screen.getByText(label)).toBeInTheDocument();
    });
  });

  it('applies custom className', () => {
    const { container } = render(
      <PriorityBadge priority={PRIORITY.CRITICAL} className="custom-class" />,
    );
    expect(container.firstChild).toHaveClass('custom-class');
  });
});
