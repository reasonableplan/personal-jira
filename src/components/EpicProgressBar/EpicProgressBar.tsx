import type { EpicProgress } from "../../types/issue";
import styles from "./EpicProgressBar.module.css";

interface EpicProgressBarProps {
  progress: EpicProgress;
  loading?: boolean;
  className?: string;
}

export function EpicProgressBar({ progress, loading, className }: EpicProgressBarProps) {
  const { total, done, in_progress, percentage } = progress;
  const inProgressPct = total > 0 ? Math.round((in_progress / total) * 100) : 0;

  if (loading) {
    return (
      <div className={`${styles.container} ${className ?? ""}`} data-testid="progress-skeleton">
        <div className={styles.skeleton} />
      </div>
    );
  }

  return (
    <div className={`${styles.container} ${className ?? ""}`}>
      <div className={styles.header}>
        <span className={styles.percentage}>{percentage}%</span>
        <span className={styles.count}>{done} / {total} done</span>
      </div>
      <div className={styles.track} role="progressbar" aria-valuenow={percentage} aria-valuemin={0} aria-valuemax={100}>
        <div
          className={styles.segmentDone}
          data-testid="progress-done"
          style={{ width: `${percentage}%` }}
        />
        <div
          className={styles.segmentInProgress}
          data-testid="progress-in-progress"
          style={{ width: `${inProgressPct}%` }}
        />
      </div>
    </div>
  );
}
