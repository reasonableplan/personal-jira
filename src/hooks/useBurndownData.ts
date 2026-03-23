import { useState, useEffect } from 'react';
import type { BurndownData, UseBurndownDataReturn } from '../types/burndown';

const API_BASE = '/api/v1/sprints';

export function useBurndownData(sprintId: string): UseBurndownDataReturn {
  const [data, setData] = useState<BurndownData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sprintId) return;

    let cancelled = false;
    setIsLoading(true);
    setError(null);

    fetch(`${API_BASE}/${sprintId}/burndown`)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`번다운 데이터 로드 실패: ${res.status} ${res.statusText}`);
        }
        return res.json();
      })
      .then((json: BurndownData) => {
        if (!cancelled) setData(json);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [sprintId]);

  return { data, isLoading, error };
}
