import { useQuery } from '@tanstack/react-query';

import { getStories, getStory } from '@/api/stories';
import type { PaginationParams } from '@/types/common';

export const storyKeys = {
  all: ['stories'] as const,
  lists: () => [...storyKeys.all, 'list'] as const,
  list: (epicId: string, params?: PaginationParams) =>
    [...storyKeys.lists(), epicId, params] as const,
  details: () => [...storyKeys.all, 'detail'] as const,
  detail: (id: string) => [...storyKeys.details(), id] as const,
};

export const useStories = (epicId: string, params?: PaginationParams) => {
  return useQuery({
    queryKey: storyKeys.list(epicId, params),
    queryFn: () => getStories(epicId, params),
    enabled: !!epicId,
  });
};

export const useStory = (id: string) => {
  return useQuery({
    queryKey: storyKeys.detail(id),
    queryFn: () => getStory(id),
    enabled: !!id,
  });
};
