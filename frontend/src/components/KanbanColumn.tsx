import { useDroppable } from '@dnd-kit/core';
import type { Issue, IssueStatus } from '@/types/issue';
import { COLUMN_LABELS } from '@/types/issue';
import { IssueCard } from './IssueCard';
import styles from './KanbanColumn.module.css';

interface KanbanColumnProps {
  status: IssueStatus;
  issues: Issue[];
}

export function KanbanColumn({ status, issues }: KanbanColumnProps) {
  const { setNodeRef, isOver } = useDroppable({ id: status });

  return (
    <div
      className={`${styles.column} ${isOver ? styles.over : ''}`}
      data-testid={`column-${status}`}
    >
      <div className={styles.header}>
        <h2 className={styles.title}>{COLUMN_LABELS[status]}</h2>
        <span className={styles.count}>{issues.length}</span>
      </div>
      <div ref={setNodeRef} className={styles.body}>
        {issues.map((issue) => (
          <IssueCard key={issue.id} issue={issue} />
        ))}
      </div>
    </div>
  );
}
