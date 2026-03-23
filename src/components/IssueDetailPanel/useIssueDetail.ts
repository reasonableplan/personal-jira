import { useState, useEffect, useCallback } from 'react';
import type { Comment, ActivityLog, Artifact } from '../../types/issue';
import type { TabKey } from './constants';
import { API_BASE } from './constants';

export function useIssueDetail(issueId: string | null) {
  const [activeTab, setActiveTab] = useState<TabKey>('detail');
  const [comments, setComments] = useState<Comment[]>([]);
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [commentsLoading, setCommentsLoading] = useState(false);
  const [logsLoading, setLogsLoading] = useState(false);
  const [artifactsLoading, setArtifactsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async (id: string) => {
    setCommentsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/issues/${id}/comments`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setComments(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      console.error('Failed to load issue details:', message);
      setError('Failed to load issue details');
    } finally {
      setCommentsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!issueId) return;
    setActiveTab('detail');
    setComments([]);
    setLogs([]);
    setArtifacts([]);
    fetchData(issueId);
  }, [issueId, fetchData]);

  return {
    activeTab,
    setActiveTab,
    comments,
    logs,
    artifacts,
    commentsLoading,
    logsLoading,
    artifactsLoading,
    error,
  };
}
