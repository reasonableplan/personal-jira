import type { ActivityLog } from '../../../types/issue';
import { LoadingSpinner } from '../LoadingSpinner';
import styles from './Tabs.module.css';

interface LogsTabProps {
  logs: ActivityLog[];
  loading: boolean;
}

export function LogsTab({ logs, loading }: LogsTabProps) {
  if (loading) return <LoadingSpinner />;

  return (
    <div data-testid="tab-content-logs">
      {logs.length === 0 ? (
        <p className={styles.empty}>활동 로그가 없습니다</p>
      ) : (
        <ul className={styles.timeline}>
          {logs.map((log) => (
            <li key={log.id} className={styles.timelineItem}>
              <div className={styles.listHeader}>
                <span className={styles.action}>{log.action}</span>
                <span className={styles.actor}>{log.actor}</span>
                <time className={styles.time}>{log.created_at.slice(0, 16).replace('T', ' ')}</time>
              </div>
              <p className={styles.listContent}>{log.detail}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
