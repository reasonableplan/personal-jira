import { useMutation, useQueryClient } from '@tanstack/react-query';

import { createStory, deleteStory, updateStory } from '@/api/stories';
import { storyKeys } from '@/hooks/queries/useStories';
import type { CreateStoryRequest, UpdateStoryRequest } from '@/types/story';

export const useCreateStory = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: CreateStoryRequest) => createStory(body),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({
        queryKey: storyKeys.list(variables.epic_id),
      });
    },
  });
};

export const useUpdateStory = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: UpdateStoryRequest }) =>
      updateStory(id, body),
    onSuccess: (data) => {
      queryClient.setQueryData(storyKeys.detail(data.id), data);
      queryClient.invalidateQueries({ queryKey: storyKeys.lists() });
    },
  });
};

export const useDeleteStory = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteStory(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: storyKeys.lists() });
    },
  });
};
