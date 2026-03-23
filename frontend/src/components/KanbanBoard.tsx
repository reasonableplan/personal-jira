import { DndContext, DragOverlay, pointerWithin } from '@dnd-kit/core';
import type { DragStartEvent, DragEndEvent } from '@dnd-kit/core';
import { useState, useCallback, useMemo } from 'react';
import { useIssues } from '@/hooks/useIssues';
import { KanbanColumn } from './KanbanColumn';
import { IssueCard } from './IssueCard';
import { COLUMN_ORDER } from '@/types/issue';
import type { Issue, IssueStatus } from '@/types/issue';
import styles from './KanbanBoard.module.css';

export function KanbanBoard() {
  const { issues, loading, error, moveIssue } = useIssues();
  const [activeIssue, setActiveIssue] = useState<Issue | null>(null);

  const issuesByStatus = useMemo(() => {
    const grouped: Record<IssueStatus, Issue[]> = {
      Backlog: [],
      Ready: [],
      InProgress: [],
      InReview: [],
      Done: [],
      Blocked: [],
      Abandoned: [],
    };
    for (const issue of issues) {
      grouped[issue.status].push(issue);
    }
    return grouped;
  }, [issues]);

  const handleDragStart = useCallback((event: DragStartEvent) => {
    const issue = event.active.data.current?.issue as Issue | undefined;
    if (issue) setActiveIssue(issue);
  }, []);

  const handleDragEnd = useCallback(
    (event: DragEndEvent) => {
      setActiveIssue(null);
      const { active, over } = event;
      if (!over) return;

      const issueId = active.id as string;
      const newStatus = over.id as IssueStatus;
      const currentIssue = issues.find((i) => i.id === issueId);

      if (currentIssue && currentIssue.status !== newStatus) {
        void moveIssue(issueId, newStatus);
      }
    },
    [issues, moveIssue],
  );

  const handleDragCancel = useCallback(() => {
    setActiveIssue(null);
  }, []);

  if (loading) {
    return (
      <div className={styles.center} data-testid="loading-spinner">
        <div className={styles.spinner} />
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.center} data-testid="error-message">
        <p className={styles.error}>{error}</p>
      </div>
    );
  }

  return (
    <DndContext
      collisionDetection={pointerWithin}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragCancel={handleDragCancel}
    >
      <div className={styles.board} data-testid="kanban-board">
        {COLUMN_ORDER.map((status) => (
          <KanbanColumn
            key={status}
            status={status}
            issues={issuesByStatus[status]}
          />
        ))}
      </div>
      <DragOverlay>
        {activeIssue ? <IssueCard issue={activeIssue} /> : null}
      </DragOverlay>
    </DndContext>
  );
}
