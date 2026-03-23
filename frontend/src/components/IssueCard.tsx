import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import type { Issue } from '@/types/issue';
import { PRIORITY_COLORS } from '@/types/issue';
import styles from './IssueCard.module.css';

interface IssueCardProps {
  issue: Issue;
}

export function IssueCard({ issue }: IssueCardProps) {
  const { attributes, listeners, setNodeRef, transform, isDragging } =
    useDraggable({ id: issue.id, data: { issue } });

  const style = {
    transform: CSS.Translate.toString(transform),
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={styles.card}
      data-testid={`issue-card-${issue.id}`}
      {...listeners}
      {...attributes}
    >
      <div className={styles.header}>
        <span className={styles.title}>{issue.title}</span>
        <span
          className={styles.priority}
          style={{ backgroundColor: PRIORITY_COLORS[issue.priority] }}
        >
          {issue.priority}
        </span>
      </div>
      {issue.description && (
        <p className={styles.description} data-testid="card-description">
          {issue.description}
        </p>
      )}
      <div className={styles.footer}>
        <span className={styles.id}>{issue.id.slice(0, 8)}</span>
      </div>
    </div>
  );
}
