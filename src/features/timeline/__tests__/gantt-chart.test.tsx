import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { GanttChart } from '../gantt-chart';
import type { EpicGroup } from '../types';

vi.mock('../use-timeline', () => ({
  useTimeline: vi.fn(),
}));

import { useTimeline } from '../use-timeline';

const mockedUseTimeline = vi.mocked(useTimeline);

const MOCK_GROUPS: EpicGroup[] = [
  {
    epicId: 'e1',
    epicTitle: 'Auth Epic',
    startDate: '2026-03-01',
    endDate: '2026-03-10',
    issues: [
      { id: '1', title: 'Auth API', epicId: 'e1', epicTitle: 'Auth Epic', status: 'IN_PROGRESS', priority: 'HIGH', startDate: '2026-03-01', dueDate: '2026-03-10' },
    ],
  },
];

describe('GanttChart', () => {
  it('renders loading state', () => {
    mockedUseTimeline.mockReturnValue({
      epicGroups: [],
      timelineStart: '',
      totalDays: 0,
      isLoading: true,
      error: null,
    });

    render(<GanttChart />);
    expect(screen.getByText('Loading timeline...')).toBeInTheDocument();
  });

  it('renders error state', () => {
    mockedUseTimeline.mockReturnValue({
      epicGroups: [],
      timelineStart: '',
      totalDays: 0,
      isLoading: false,
      error: 'Failed to fetch',
    });

    render(<GanttChart />);
    expect(screen.getByText('Failed to fetch')).toBeInTheDocument();
  });

  it('renders empty state', () => {
    mockedUseTimeline.mockReturnValue({
      epicGroups: [],
      timelineStart: '',
      totalDays: 0,
      isLoading: false,
      error: null,
    });

    render(<GanttChart />);
    expect(screen.getByText('No timeline data available')).toBeInTheDocument();
  });

  it('renders epic groups with issue bars', () => {
    mockedUseTimeline.mockReturnValue({
      epicGroups: MOCK_GROUPS,
      timelineStart: '2026-03-01',
      totalDays: 14,
      isLoading: false,
      error: null,
    });

    render(<GanttChart />);
    expect(screen.getByText('Auth Epic')).toBeInTheDocument();
    expect(screen.getByText('Auth API')).toBeInTheDocument();
  });

  it('renders date header columns', () => {
    mockedUseTimeline.mockReturnValue({
      epicGroups: MOCK_GROUPS,
      timelineStart: '2026-03-01',
      totalDays: 3,
      isLoading: false,
      error: null,
    });

    render(<GanttChart />);
    expect(screen.getByText('3/1')).toBeInTheDocument();
    expect(screen.getByText('3/2')).toBeInTheDocument();
    expect(screen.getByText('3/3')).toBeInTheDocument();
  });
});
