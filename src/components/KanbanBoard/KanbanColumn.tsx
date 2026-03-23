import type { Issue } from "../../types/issue";
import { IssueStatus, STATUS_LABELS } from "../../types/issue";
import type { DragState } from "../../hooks/useKanbanDrag";
import { KanbanCard } from "./KanbanCard";
import styles from "./KanbanBoard.module.css";

interface KanbanColumnProps {
  status: IssueStatus;
  issues: Issue[];
  dragState: DragState;
  onDragStart: (id: string) => void;
  onDragOver: (id: string) => void;
  onDrop: () => void;
  onDragEnd: () => void;
}

export function KanbanColumn({
  status,
  issues,
  dragState,
  onDragStart,
  onDragOver,
  onDrop,
  onDragEnd,
}: KanbanColumnProps) {
  const sorted = [...issues].sort((a, b) => a.priority_order - b.priority_order);

  return (
    <div
      className={styles.column}
      data-testid={`kanban-column-${status}`}
      onDrop={(e) => {
        e.preventDefault();
        onDrop();
      }}
      onDragOver={(e) => e.preventDefault()}
      onDragEnd={onDragEnd}
    >
      <div className={styles.columnHeader}>
        <span className={styles.columnTitle}>{STATUS_LABELS[status]}</span>
        <span className={styles.columnCount}>{issues.length}</span>
      </div>
      <div className={styles.columnBody}>
        {sorted.map((issue) => (
          <KanbanCard
            key={issue.id}
            issue={issue}
            onDragStart={onDragStart}
            onDragOver={onDragOver}
            isDragging={dragState.draggedId === issue.id}
            isDragOver={dragState.overId === issue.id}
          />
        ))}
      </div>
    </div>
  );
}
