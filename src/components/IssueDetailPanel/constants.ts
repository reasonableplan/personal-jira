export const TAB_KEYS = ['detail', 'comments', 'logs', 'artifacts'] as const;
export type TabKey = (typeof TAB_KEYS)[number];

export const TAB_LABELS: Record<TabKey, string> = {
  detail: '상세',
  comments: '코멘트',
  logs: '로그',
  artifacts: '아티팩트',
};

export const API_BASE = '/api/v1';
