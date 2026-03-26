import { useMutation, useQueryClient } from '@tanstack/react-query';

import {
  createLabel,
  deleteLabel,
  updateLabel,
} from '@/api/labels';
import type { CreateLabelRequest, UpdateLabelRequest } from '@/api/labels';
import { labelKeys } from '@/hooks/queries/useLabels';

export const useCreateLabel = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: CreateLabelRequest) => createLabel(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: labelKeys.lists() });
    },
  });
};

export const useUpdateLabel = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: UpdateLabelRequest }) =>
      updateLabel(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: labelKeys.lists() });
    },
  });
};

export const useDeleteLabel = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteLabel(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: labelKeys.lists() });
    },
  });
};
