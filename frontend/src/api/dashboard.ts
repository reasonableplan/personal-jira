import { apiClient } from '@/api/client';
import type { DashboardSummary } from '@/types/dashboard';

export const getDashboard = async (): Promise<DashboardSummary> => {
  const { data } = await apiClient.get<DashboardSummary>(
    '/dashboard/summary',
  );
  return data;
};
