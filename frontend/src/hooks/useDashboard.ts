import { useEffect, useState, useCallback } from 'react';
import type { DashboardStats, WsEvent } from '../types/issue';
import { api } from '../services/api';

interface UseDashboardReturn {
  stats: DashboardStats | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useDashboard(): UseDashboardReturn {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getDashboardStats();
      setStats(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load dashboard';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { stats, loading, error, refresh };
}

export function applyWsEventToStats(stats: DashboardStats, event: WsEvent): DashboardStats {
  const updated = { ...stats, status_counts: { ...stats.status_counts }, priority_counts: { ...stats.priority_counts } };
  const { type, payload } = event;

  if (type === 'issue_created') {
    updated.status_counts[payload.status] = (updated.status_counts[payload.status] ?? 0) + 1;
    updated.priority_counts[payload.priority] = (updated.priority_counts[payload.priority] ?? 0) + 1;
  }

  if (type === 'issue_status_changed') {
    updated.status_counts[payload.status] = (updated.status_counts[payload.status] ?? 0) + 1;
  }

  return updated;
}
