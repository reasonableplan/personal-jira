export const TOAST_TYPES = ['success', 'error', 'warning', 'info'] as const;
export type ToastType = (typeof TOAST_TYPES)[number];

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

export interface ToastInput {
  type: ToastType;
  message: string;
  duration?: number;
}

export const DEFAULT_TOAST_DURATION = 5000;
export const MAX_TOASTS = 5;
