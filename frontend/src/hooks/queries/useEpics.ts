import { useQuery } from '@tanstack/react-query';

import { getEpic, getEpics } from '@/api/epics';
import type { PaginationParams } from '@/types/common';

export const epicKeys = {
  all: ['epics'] as const,
  lists: () => [...epicKeys.all, 'list'] as const,
  list: (params?: PaginationParams) =>
    [...epicKeys.lists(), params] as const,
  details: () => [...epicKeys.all, 'detail'] as const,
  detail: (id: string) => [...epicKeys.details(), id] as const,
};

export const useEpics = (params?: PaginationParams) => {
  return useQuery({
    queryKey: epicKeys.list(params),
    queryFn: () => getEpics(params),
  });
};

export const useEpic = (id: string) => {
  return useQuery({
    queryKey: epicKeys.detail(id),
    queryFn: () => getEpic(id),
    enabled: !!id,
  });
};
