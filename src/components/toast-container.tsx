import { useToast } from '../hooks/use-toast';
import type { ToastType } from '../types/toast';
import styles from './toast-container.module.css';

const ICON_MAP: Record<ToastType, string> = {
  success: '\u2713',
  error: '\u2717',
  warning: '\u26A0',
  info: '\u2139',
};

export function ToastContainer() {
  const { toasts, removeToast } = useToast();

  return (
    <div data-testid="toast-container" className={styles.container}>
      {toasts.map((toast) => (
        <div
          key={toast.id}
          data-testid="toast-item"
          className={`${styles.toast} ${styles[toast.type]}`}
          role="alert"
        >
          <span data-testid="toast-icon" className={styles.icon}>
            {ICON_MAP[toast.type]}
          </span>
          <span className={styles.message}>{toast.message}</span>
          <button
            className={styles.dismiss}
            onClick={() => removeToast(toast.id)}
            aria-label="dismiss"
            type="button"
          >
            \u00D7
          </button>
        </div>
      ))}
    </div>
  );
}
