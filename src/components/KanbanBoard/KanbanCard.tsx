import type { Issue } from "../../types/issue";
import styles from "./KanbanBoard.module.css";

interface KanbanCardProps {
  issue: Issue;
  onDragStart: (id: string) => void;
  onDragOver: (id: string) => void;
  isDragging?: boolean;
  isDragOver?: boolean;
}

export function KanbanCard({ issue, onDragStart, onDragOver, isDragging, isDragOver }: KanbanCardProps) {
  const classNames = [
    styles.card,
    isDragging ? styles.dragging : "",
    isDragOver ? styles.dragOver : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div
      className={classNames}
      data-testid={`kanban-card-${issue.id}`}
      draggable
      onDragStart={() => onDragStart(issue.id)}
      onDragOver={(e) => {
        e.preventDefault();
        onDragOver(issue.id);
      }}
    >
      <div className={styles.cardHeader}>
        <span className={styles.cardTitle}>{issue.title}</span>
      </div>
      <div className={styles.cardMeta}>
        <span className={`${styles.badge} ${styles[`badge_${issue.issue_type}`] ?? ""}`}>
          {issue.issue_type}
        </span>
        <span className={`${styles.badge} ${styles[`priority_${issue.priority}`] ?? ""}`}>
          {issue.priority}
        </span>
      </div>
    </div>
  );
}
