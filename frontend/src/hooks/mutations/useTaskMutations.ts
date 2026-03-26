import { useMutation, useQueryClient } from '@tanstack/react-query';

import { createTask, deleteTask, updateTask, updateTaskStatus } from '@/api/tasks';
import { taskKeys } from '@/hooks/queries/useTasks';
import type { PaginatedResponse } from '@/types/common';
import type {
  CreateTaskRequest,
  Task,
  TaskStatus,
  UpdateTaskRequest,
} from '@/types/task';

export const useCreateTask = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: CreateTaskRequest) => createTask(body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });
};

export const useUpdateTask = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: UpdateTaskRequest }) =>
      updateTask(id, body),
    onSuccess: (data) => {
      queryClient.setQueryData(taskKeys.detail(data.id), data);
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });
};

export const useUpdateTaskStatus = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: TaskStatus }) =>
      updateTaskStatus(id, { status }),
    onMutate: async ({ id, status }) => {
      await queryClient.cancelQueries({ queryKey: taskKeys.lists() });
      await queryClient.cancelQueries({ queryKey: taskKeys.detail(id) });

      const previousDetail = queryClient.getQueryData<Task>(
        taskKeys.detail(id),
      );
      const previousLists = queryClient.getQueriesData<
        PaginatedResponse<Task>
      >({ queryKey: taskKeys.lists() });

      if (previousDetail) {
        queryClient.setQueryData<Task>(taskKeys.detail(id), {
          ...previousDetail,
          status,
        });
      }

      queryClient.setQueriesData<PaginatedResponse<Task>>(
        { queryKey: taskKeys.lists() },
        (old) => {
          if (!old) return old;
          return {
            ...old,
            items: old.items.map((task) =>
              task.id === id ? { ...task, status } : task,
            ),
          };
        },
      );

      return { previousDetail, previousLists };
    },
    onError: (_err, { id }, context) => {
      if (context?.previousDetail) {
        queryClient.setQueryData(taskKeys.detail(id), context.previousDetail);
      }
      if (context?.previousLists) {
        for (const [key, data] of context.previousLists) {
          queryClient.setQueryData(key, data);
        }
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });
};

export const useDeleteTask = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteTask(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });
};
