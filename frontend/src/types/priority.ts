export const PRIORITY = {
  CRITICAL: 1,
  HIGH: 2,
  MEDIUM: 3,
  LOW: 4,
  LOWEST: 5,
} as const;

export type Priority = (typeof PRIORITY)[keyof typeof PRIORITY];

export const PRIORITY_CONFIG: Record<
  Priority,
  { label: string; className: string }
> = {
  [PRIORITY.CRITICAL]: {
    label: 'Critical',
    className: 'bg-red-100 text-red-800 border-red-200',
  },
  [PRIORITY.HIGH]: {
    label: 'High',
    className: 'bg-orange-100 text-orange-800 border-orange-200',
  },
  [PRIORITY.MEDIUM]: {
    label: 'Medium',
    className: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  },
  [PRIORITY.LOW]: {
    label: 'Low',
    className: 'bg-blue-100 text-blue-800 border-blue-200',
  },
  [PRIORITY.LOWEST]: {
    label: 'Lowest',
    className: 'bg-gray-100 text-gray-800 border-gray-200',
  },
};
