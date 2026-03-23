import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { GanttBar } from '../gantt-bar';
import type { TimelineIssue } from '../types';

const ISSUE: TimelineIssue = {
  id: '1',
  title: 'Implement Auth',
  epicId: 'e1',
  epicTitle: 'Auth',
  status: 'IN_PROGRESS',
  priority: 'HIGH',
  startDate: '2026-03-03',
  dueDate: '2026-03-08',
};

describe('GanttBar', () => {
  it('renders bar with issue title', () => {
    render(<GanttBar issue={ISSUE} timelineStart="2026-03-01" />);
    expect(screen.getByText('Implement Auth')).toBeInTheDocument();
  });

  it('applies correct positioning styles', () => {
    const { container } = render(<GanttBar issue={ISSUE} timelineStart="2026-03-01" />);
    const bar = container.querySelector('[data-testid="gantt-bar-1"]');
    expect(bar).toBeTruthy();
    expect(bar?.getAttribute('style')).toContain('left:');
    expect(bar?.getAttribute('style')).toContain('width:');
  });

  it('shows tooltip on hover', async () => {
    const user = userEvent.setup();
    render(<GanttBar issue={ISSUE} timelineStart="2026-03-01" />);

    const bar = screen.getByTestId('gantt-bar-1');
    await user.hover(bar);

    expect(screen.getByText('2026-03-03 ~ 2026-03-08')).toBeInTheDocument();
    expect(screen.getByText('HIGH')).toBeInTheDocument();
  });

  it('applies status-based color', () => {
    const { container } = render(<GanttBar issue={ISSUE} timelineStart="2026-03-01" />);
    const bar = container.querySelector('[data-testid="gantt-bar-1"]');
    expect(bar?.className).toContain('bg-blue-500');
  });
});
