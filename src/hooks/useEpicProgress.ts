import { useState, useEffect, useCallback } from "react";
import type { Issue, EpicProgress } from "../types/issue";
import { IssueStatus } from "../types/issue";
import { fetchEpicChildren } from "../api/issues";

const IN_PROGRESS_STATUSES = new Set<IssueStatus>([
  IssueStatus.IN_PROGRESS,
  IssueStatus.IN_REVIEW,
]);

export function computeProgress(children: Issue[]): EpicProgress {
  const total = children.length;
  if (total === 0) return { total: 0, done: 0, in_progress: 0, percentage: 0 };

  const done = children.filter((c) => c.status === IssueStatus.DONE).length;
  const in_progress = children.filter((c) => IN_PROGRESS_STATUSES.has(c.status)).length;
  const percentage = Math.round((done / total) * 100);

  return { total, done, in_progress, percentage };
}

export function useEpicProgress(epicId: string) {
  const [progress, setProgress] = useState<EpicProgress>({
    total: 0,
    done: 0,
    in_progress: 0,
    percentage: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const children = await fetchEpicChildren(epicId);
      setProgress(computeProgress(children));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load progress");
    } finally {
      setLoading(false);
    }
  }, [epicId]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { progress, loading, error, refresh };
}
