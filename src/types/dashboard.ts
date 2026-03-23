export type WidgetSize = 'small' | 'medium' | 'large';

export type WidgetType = 'stats' | 'chart' | 'list' | 'activity';

export interface WidgetPosition {
  x: number;
  y: number;
}

export interface WidgetConfig {
  id: string;
  type: WidgetType;
  title: string;
  size: WidgetSize;
  position: WidgetPosition;
  dataSource: string;
}

export interface WidgetData {
  value?: number;
  label?: string;
  items?: Array<{ id: string; text: string }>;
  chartData?: Array<{ x: string; y: number }>;
}
