import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { BurndownChart } from '../BurndownChart';
import type { BurndownData } from '../../../types/burndown';

vi.mock('recharts', () => {
  const MockResponsiveContainer = ({ children }: { children: React.ReactNode }) => (
    <div data-testid="responsive-container">{children}</div>
  );
  const MockLineChart = ({ children, data }: { children: React.ReactNode; data: unknown[] }) => (
    <div data-testid="line-chart" data-points={data.length}>{children}</div>
  );
  const MockLine = ({ dataKey, name }: { dataKey: string; name: string }) => (
    <div data-testid={`line-${dataKey}`} data-name={name} />
  );
  const MockXAxis = ({ dataKey }: { dataKey: string }) => (
    <div data-testid="x-axis" data-key={dataKey} />
  );
  const MockYAxis = () => <div data-testid="y-axis" />;
  const MockTooltip = () => <div data-testid="tooltip" />;
  const MockLegend = () => <div data-testid="legend" />;
  const MockCartesianGrid = () => <div data-testid="cartesian-grid" />;
  const MockReferenceLine = ({ label }: { label?: string }) => (
    <div data-testid="reference-line" data-label={label} />
  );
  return {
    ResponsiveContainer: MockResponsiveContainer,
    LineChart: MockLineChart,
    Line: MockLine,
    XAxis: MockXAxis,
    YAxis: MockYAxis,
    Tooltip: MockTooltip,
    Legend: MockLegend,
    CartesianGrid: MockCartesianGrid,
    ReferenceLine: MockReferenceLine,
  };
});

const MOCK_DATA: BurndownData = {
  sprintName: 'Sprint 1',
  startDate: '2026-03-01',
  endDate: '2026-03-14',
  totalPoints: 40,
  points: [
    { date: '2026-03-01', ideal: 40, actual: 40 },
    { date: '2026-03-04', ideal: 30, actual: 35 },
    { date: '2026-03-07', ideal: 20, actual: 25 },
    { date: '2026-03-10', ideal: 10, actual: 15 },
    { date: '2026-03-14', ideal: 0, actual: 5 },
  ],
};

const EMPTY_DATA: BurndownData = {
  sprintName: 'Empty Sprint',
  startDate: '2026-03-01',
  endDate: '2026-03-14',
  totalPoints: 0,
  points: [],
};

describe('BurndownChart', () => {
  it('renders chart with sprint name', () => {
    render(<BurndownChart data={MOCK_DATA} />);
    expect(screen.getByText('Sprint 1')).toBeDefined();
  });

  it('renders line chart with correct data points', () => {
    render(<BurndownChart data={MOCK_DATA} />);
    const chart = screen.getByTestId('line-chart');
    expect(chart.getAttribute('data-points')).toBe('5');
  });

  it('renders ideal and actual lines', () => {
    render(<BurndownChart data={MOCK_DATA} />);
    expect(screen.getByTestId('line-ideal')).toBeDefined();
    expect(screen.getByTestId('line-actual')).toBeDefined();
  });

  it('renders axes and grid', () => {
    render(<BurndownChart data={MOCK_DATA} />);
    expect(screen.getByTestId('x-axis')).toBeDefined();
    expect(screen.getByTestId('y-axis')).toBeDefined();
    expect(screen.getByTestId('cartesian-grid')).toBeDefined();
  });

  it('renders tooltip and legend', () => {
    render(<BurndownChart data={MOCK_DATA} />);
    expect(screen.getByTestId('tooltip')).toBeDefined();
    expect(screen.getByTestId('legend')).toBeDefined();
  });

  it('shows empty state when no data points', () => {
    render(<BurndownChart data={EMPTY_DATA} />);
    expect(screen.getByText('데이터가 없습니다')).toBeDefined();
  });

  it('shows date range subtitle', () => {
    render(<BurndownChart data={MOCK_DATA} />);
    expect(screen.getByText('2026-03-01 → 2026-03-14')).toBeDefined();
  });

  it('renders with custom height', () => {
    render(<BurndownChart data={MOCK_DATA} height={500} />);
    const container = screen.getByTestId('responsive-container');
    expect(container).toBeDefined();
  });

  it('displays total points badge', () => {
    render(<BurndownChart data={MOCK_DATA} />);
    expect(screen.getByText('40 포인트')).toBeDefined();
  });

  it('renders reference line for today when within sprint range', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-03-07'));
    render(<BurndownChart data={MOCK_DATA} />);
    expect(screen.getByTestId('reference-line')).toBeDefined();
    vi.useRealTimers();
  });
});
