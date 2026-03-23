import { useState } from 'react';
import type { WidgetConfig, WidgetData, WidgetSize } from '../types/dashboard';

const SIZE_OPTIONS: WidgetSize[] = ['small', 'medium', 'large'];

interface DashboardWidgetProps {
  config: WidgetConfig;
  onRemove: (id: string) => void;
  onResize: (id: string, size: WidgetSize) => void;
  onMove: (id: string, position: { x: number; y: number }) => void;
  loading?: boolean;
  error?: string;
  data?: WidgetData;
  onRetry?: () => void;
}

export function DashboardWidget({
  config,
  onRemove,
  onResize,
  onMove,
  loading,
  error,
  data,
  onRetry,
}: DashboardWidgetProps) {
  const [showSizeMenu, setShowSizeMenu] = useState(false);

  if (loading) {
    return (
      <div
        className={`widget widget-${config.size}`}
        role="region"
        aria-label={config.title}
        data-testid="widget-skeleton"
      >
        <div className="widget-header">
          <h3>{config.title}</h3>
        </div>
        <div className="widget-body skeleton" />
      </div>
    );
  }

  return (
    <div className={`widget widget-${config.size}`} role="region" aria-label={config.title}>
      <div className="widget-header">
        <h3>{config.title}</h3>
        <div className="widget-actions">
          <button
            aria-label="Resize widget"
            onClick={() => setShowSizeMenu((prev) => !prev)}
          >
            Resize
          </button>
          <button aria-label="Remove widget" onClick={() => onRemove(config.id)}>
            ×
          </button>
        </div>
      </div>

      {showSizeMenu && (
        <ul className="size-menu">
          {SIZE_OPTIONS.map((size) => (
            <li key={size}>
              <button
                onClick={() => {
                  onResize(config.id, size);
                  setShowSizeMenu(false);
                }}
              >
                {size.charAt(0).toUpperCase() + size.slice(1)}
              </button>
            </li>
          ))}
        </ul>
      )}

      <div className="widget-body">
        {error ? (
          <div className="widget-error">
            <p>{error}</p>
            <button onClick={onRetry}>Retry</button>
          </div>
        ) : config.type === 'stats' && data ? (
          <div className="stats-content">
            <span className="stats-value">{data.value}</span>
            <span className="stats-label">{data.label}</span>
          </div>
        ) : config.type === 'chart' ? (
          <div data-testid="chart-container" className="chart-content" />
        ) : null}
      </div>
    </div>
  );
}
