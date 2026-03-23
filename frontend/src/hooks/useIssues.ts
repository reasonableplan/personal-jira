import { useCallback, useEffect, useState } from 'react';
import { issueApi } from '@/services/api';
import type { Issue, IssueStatus } from '@/types/issue';

export interface UseIssuesReturn {
  issues: Issue[];
  loading: boolean;
  error: string | null;
  moveIssue: (issueId: string, newStatus: IssueStatus) => Promise<void>;
  refresh: () => Promise<void>;
}

export function useIssues(): UseIssuesReturn {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await issueApi.list();
      setIssues(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load issues';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  const moveIssue = useCallback(async (issueId: string, newStatus: IssueStatus) => {
    setIssues((prev) =>
      prev.map((issue) =>
        issue.id === issueId ? { ...issue, status: newStatus } : issue,
      ),
    );

    try {
      const updated = await issueApi.transition(issueId, newStatus);
      setIssues((prev) =>
        prev.map((issue) => (issue.id === issueId ? updated : issue)),
      );
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to move issue';
      setError(message);
      setIssues((prev) =>
        prev.map((issue) => {
          if (issue.id === issueId) {
            const original = prev.find((i) => i.id === issueId);
            return original ?? issue;
          }
          return issue;
        }),
      );
      await refresh();
    }
  }, [refresh]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return { issues, loading, error, moveIssue, refresh };
}
