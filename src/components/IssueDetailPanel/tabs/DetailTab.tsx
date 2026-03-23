import type { Issue } from '../../../types/issue';
import styles from './Tabs.module.css';

interface DetailTabProps {
  issue: Issue;
}

function formatDate(iso: string): string {
  return iso.slice(0, 10);
}

export function DetailTab({ issue }: DetailTabProps) {
  return (
    <div data-testid="tab-content-detail">
      <div className={styles.metaGrid}>
        <div className={styles.metaItem}>
          <span className={styles.metaLabel}>상태</span>
          <span className={styles.badge}>{issue.status}</span>
        </div>
        <div className={styles.metaItem}>
          <span className={styles.metaLabel}>우선순위</span>
          <span className={styles.badge}>{issue.priority}</span>
        </div>
        <div className={styles.metaItem}>
          <span className={styles.metaLabel}>유형</span>
          <span className={styles.badge}>{issue.issue_type}</span>
        </div>
        <div className={styles.metaItem}>
          <span className={styles.metaLabel}>담당자</span>
          <span>{issue.assignee_id ?? '미할당'}</span>
        </div>
        <div className={styles.metaItem}>
          <span className={styles.metaLabel}>생성일</span>
          <span>{formatDate(issue.created_at)}</span>
        </div>
        <div className={styles.metaItem}>
          <span className={styles.metaLabel}>수정일</span>
          <span>{formatDate(issue.updated_at)}</span>
        </div>
      </div>
      <div className={styles.section}>
        <h3 className={styles.sectionTitle}>설명</h3>
        <p className={styles.description}>{issue.description}</p>
      </div>
    </div>
  );
}
