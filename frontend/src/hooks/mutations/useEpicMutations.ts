import { useMutation, useQueryClient } from '@tanstack/react-query';

import { createEpic, deleteEpic, updateEpic } from '@/api/epics';
import { epicKeys } from '@/hooks/queries/useEpics';
import type { CreateEpicRequest, UpdateEpicRequest } from '@/types/epic';

export const useCreateEpic = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: CreateEpicRequest) => createEpic(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: epicKeys.lists() });
    },
  });
};

export const useUpdateEpic = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: UpdateEpicRequest }) =>
      updateEpic(id, body),
    onSuccess: (data) => {
      queryClient.setQueryData(epicKeys.detail(data.id), data);
      queryClient.invalidateQueries({ queryKey: epicKeys.lists() });
    },
  });
};

export const useDeleteEpic = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteEpic(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: epicKeys.lists() });
    },
  });
};
