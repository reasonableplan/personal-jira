import { useQuery } from '@tanstack/react-query';

import { getDashboard } from '@/api/dashboard';

export const dashboardKeys = {
  all: ['dashboard'] as const,
  summary: () => [...dashboardKeys.all, 'summary'] as const,
};

export const useDashboard = () => {
  return useQuery({
    queryKey: dashboardKeys.summary(),
    queryFn: getDashboard,
  });
};
