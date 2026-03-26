import { useQuery } from '@tanstack/react-query';

import { getLabels } from '@/api/labels';
import type { PaginationParams } from '@/types/common';

export const labelKeys = {
  all: ['labels'] as const,
  lists: () => [...labelKeys.all, 'list'] as const,
  list: (params?: PaginationParams) =>
    [...labelKeys.lists(), params] as const,
};

export const useLabels = (params?: PaginationParams) => {
  return useQuery({
    queryKey: labelKeys.list(params),
    queryFn: () => getLabels(params),
  });
};
