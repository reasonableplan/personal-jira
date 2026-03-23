import { useState, useEffect, useCallback, useMemo } from "react";
import type { Issue } from "../../types/issue";
import { IssueType, KANBAN_COLUMNS } from "../../types/issue";
import { useKanbanDrag } from "../../hooks/useKanbanDrag";
import { EpicProgressBar } from "../EpicProgressBar";
import { computeProgress } from "../../hooks/useEpicProgress";
import { KanbanColumn } from "./KanbanColumn";
import { fetchIssues } from "../../api/issues";
import styles from "./KanbanBoard.module.css";

export function KanbanBoard() {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchIssues()
      .then(setIssues)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Failed to load issues");
      })
      .finally(() => setLoading(false));
  }, []);

  const handleReorder = useCallback((updated: Issue[]) => {
    setIssues((prev) => {
      const updatedMap = new Map(updated.map((i) => [i.id, i]));
      return prev.map((i) => updatedMap.get(i.id) ?? i);
    });
  }, []);

  const { dragState, saving, handleDragStart, handleDragOver, handleDrop, handleDragEnd } =
    useKanbanDrag(handleReorder);

  const epicProgress = useMemo(() => {
    const epics = issues.filter((i) => i.issue_type === IssueType.EPIC);
    return epics.map((epic) => {
      const children = issues.filter((i) => i.parent_id === epic.id);
      return { epic, progress: computeProgress(children) };
    });
  }, [issues]);

  const issuesByStatus = useMemo(() => {
    const map = new Map<string, Issue[]>();
    for (const col of KANBAN_COLUMNS) {
      map.set(col, []);
    }
    for (const issue of issues) {
      const bucket = map.get(issue.status);
      if (bucket) bucket.push(issue);
    }
    return map;
  }, [issues]);

  if (loading) return <div className={styles.loading}>Loading...</div>;
  if (error) return <div className={styles.error}>{error}</div>;

  return (
    <div className={styles.board}>
      {epicProgress.length > 0 && (
        <div className={styles.epicSection}>
          {epicProgress.map(({ epic, progress }) => (
            <div key={epic.id} className={styles.epicItem}>
              <span className={styles.epicTitle}>{epic.title}</span>
              <EpicProgressBar progress={progress} />
            </div>
          ))}
        </div>
      )}
      <div className={styles.columns}>
        {KANBAN_COLUMNS.map((status) => (
          <KanbanColumn
            key={status}
            status={status}
            issues={issuesByStatus.get(status) ?? []}
            dragState={dragState}
            onDragStart={handleDragStart}
            onDragOver={handleDragOver}
            onDrop={() => void handleDrop(issuesByStatus.get(status) ?? [])}
            onDragEnd={handleDragEnd}
          />
        ))}
      </div>
      {saving && <div className={styles.savingIndicator}>Saving...</div>}
    </div>
  );
}
