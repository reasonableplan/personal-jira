import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { CompletionRateChart } from '../CompletionRateChart';
import type { StatusCount } from '@/types/dashboard';

const MOCK_STATUS_COUNTS: StatusCount[] = [
  { status: 'Done', count: 15 },
  { status: 'InProgress', count: 5 },
  { status: 'Backlog', count: 10 },
  { status: 'Ready', count: 3 },
  { status: 'InReview', count: 2 },
  { status: 'Blocked', count: 1 },
  { status: 'Cancelled', count: 4 },
];

describe('CompletionRateChart', () => {
  it('renders the chart title', () => {
    render(<CompletionRateChart statusCounts={MOCK_STATUS_COUNTS} completionRate={37.5} />);
    expect(screen.getByText('완료율')).toBeInTheDocument();
  });

  it('displays the completion rate percentage', () => {
    render(<CompletionRateChart statusCounts={MOCK_STATUS_COUNTS} completionRate={37.5} />);
    expect(screen.getByText('37.5%')).toBeInTheDocument();
  });

  it('renders status legend items', () => {
    render(<CompletionRateChart statusCounts={MOCK_STATUS_COUNTS} completionRate={37.5} />);
    expect(screen.getByText('Done')).toBeInTheDocument();
    expect(screen.getByText('InProgress')).toBeInTheDocument();
    expect(screen.getByText('Backlog')).toBeInTheDocument();
  });

  it('shows count next to each legend item', () => {
    render(<CompletionRateChart statusCounts={MOCK_STATUS_COUNTS} completionRate={37.5} />);
    expect(screen.getByText('15')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('renders with empty data', () => {
    render(<CompletionRateChart statusCounts={[]} completionRate={0} />);
    expect(screen.getByText('완료율')).toBeInTheDocument();
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('renders with 100% completion', () => {
    const allDone: StatusCount[] = [{ status: 'Done', count: 20 }];
    render(<CompletionRateChart statusCounts={allDone} completionRate={100} />);
    expect(screen.getByText('100%')).toBeInTheDocument();
  });
});
