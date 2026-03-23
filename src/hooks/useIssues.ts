import { useState, useEffect, useCallback } from 'react';
import type { Issue } from '@/types/issue';
import type { IssueStatus } from '@/types/issue';
import { api } from '@/api/client';

export function useIssues() {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchIssues = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.getIssues();
      setIssues(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch issues');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchIssues();
  }, [fetchIssues]);

  const createIssue = useCallback(
    async (title: string, description: string) => {
      const issue = await api.createIssue({ title, description });
      setIssues((prev) => [...prev, issue]);
      return issue;
    },
    [],
  );

  const transitionIssue = useCallback(async (id: string, status: IssueStatus) => {
    const updated = await api.transitionIssue(id, status);
    setIssues((prev) => prev.map((i) => (i.id === id ? updated : i)));
    return updated;
  }, []);

  return { issues, loading, error, createIssue, transitionIssue, refetch: fetchIssues };
}
