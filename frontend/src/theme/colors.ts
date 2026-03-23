export const THEME_COLORS = {
  primary: {
    50: '#EEF2FF',
    100: '#E0E7FF',
    200: '#C7D2FE',
    300: '#A5B4FC',
    400: '#818CF8',
    500: '#6366F1',
    600: '#4F46E5',
    700: '#4338CA',
    800: '#3730A3',
    900: '#312E81',
  },
  status: {
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#3B82F6',
  },
  priority: {
    critical: '#DC2626',
    high: '#F97316',
    medium: '#EAB308',
    low: '#22C55E',
  },
  issueStatus: {
    backlog: '#94A3B8',
    ready: '#3B82F6',
    inProgress: '#8B5CF6',
    inReview: '#F59E0B',
    done: '#10B981',
    closed: '#6B7280',
    cancelled: '#EF4444',
  },
} as const;

export type ThemeColors = typeof THEME_COLORS;
