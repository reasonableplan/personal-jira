import { useCallback, useEffect, useState } from 'react';
import type { DashboardData } from '@/types/dashboard';
import { fetchDashboardData } from '@/api/dashboard';

const POLL_INTERVAL_MS = 30_000;

interface UseDashboardResult {
  data: DashboardData | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useDashboard(): UseDashboardResult {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(() => {
    setLoading(true);
    setError(null);
    fetchDashboardData()
      .then(setData)
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : 'Failed to fetch dashboard data';
        setError(message);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    refetch();
    const interval = setInterval(refetch, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [refetch]);

  return { data, loading, error, refetch };
}
