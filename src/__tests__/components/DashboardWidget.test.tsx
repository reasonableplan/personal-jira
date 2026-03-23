import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { DashboardWidget } from '../../components/DashboardWidget';
import type { WidgetConfig } from '../../types/dashboard';

const MOCK_WIDGET: WidgetConfig = {
  id: 'widget-1',
  type: 'stats',
  title: 'Open Issues',
  size: 'medium',
  position: { x: 0, y: 0 },
  dataSource: '/api/v1/issues/stats',
};

const MOCK_CHART_WIDGET: WidgetConfig = {
  id: 'widget-2',
  type: 'chart',
  title: 'Issue Trend',
  size: 'large',
  position: { x: 1, y: 0 },
  dataSource: '/api/v1/issues/trend',
};

describe('DashboardWidget', () => {
  const onRemove = vi.fn();
  const onResize = vi.fn();
  const onMove = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders widget with title', () => {
    render(
      <DashboardWidget config={MOCK_WIDGET} onRemove={onRemove} onResize={onResize} onMove={onMove} />
    );
    expect(screen.getByText('Open Issues')).toBeInTheDocument();
  });

  it('applies correct size class', () => {
    const { container } = render(
      <DashboardWidget config={MOCK_WIDGET} onRemove={onRemove} onResize={onResize} onMove={onMove} />
    );
    expect(container.firstChild).toHaveClass('widget-medium');
  });

  it('renders chart type widget', () => {
    render(
      <DashboardWidget config={MOCK_CHART_WIDGET} onRemove={onRemove} onResize={onResize} onMove={onMove} />
    );
    expect(screen.getByText('Issue Trend')).toBeInTheDocument();
    expect(screen.getByTestId('chart-container')).toBeInTheDocument();
  });

  it('calls onRemove when close button clicked', () => {
    render(
      <DashboardWidget config={MOCK_WIDGET} onRemove={onRemove} onResize={onResize} onMove={onMove} />
    );
    fireEvent.click(screen.getByLabelText('Remove widget'));
    expect(onRemove).toHaveBeenCalledWith('widget-1');
  });

  it('shows loading state while fetching data', () => {
    render(
      <DashboardWidget config={MOCK_WIDGET} onRemove={onRemove} onResize={onResize} onMove={onMove} loading />
    );
    expect(screen.getByTestId('widget-skeleton')).toBeInTheDocument();
  });

  it('shows error state on fetch failure', () => {
    render(
      <DashboardWidget
        config={MOCK_WIDGET}
        onRemove={onRemove}
        onResize={onResize}
        onMove={onMove}
        error="Failed to load data"
      />
    );
    expect(screen.getByText('Failed to load data')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument();
  });

  it('calls onResize with new size', () => {
    render(
      <DashboardWidget config={MOCK_WIDGET} onRemove={onRemove} onResize={onResize} onMove={onMove} />
    );
    fireEvent.click(screen.getByLabelText('Resize widget'));
    fireEvent.click(screen.getByText('Large'));
    expect(onResize).toHaveBeenCalledWith('widget-1', 'large');
  });

  it('renders stats type with value and label', () => {
    render(
      <DashboardWidget
        config={MOCK_WIDGET}
        onRemove={onRemove}
        onResize={onResize}
        onMove={onMove}
        data={{ value: 42, label: 'open' }}
      />
    );
    expect(screen.getByText('42')).toBeInTheDocument();
    expect(screen.getByText('open')).toBeInTheDocument();
  });

  it('is accessible with proper aria attributes', () => {
    render(
      <DashboardWidget config={MOCK_WIDGET} onRemove={onRemove} onResize={onResize} onMove={onMove} />
    );
    const widget = screen.getByRole('region', { name: 'Open Issues' });
    expect(widget).toBeInTheDocument();
  });
});
