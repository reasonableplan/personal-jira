import { apiClient } from '@/api/client';
import type { PaginatedResponse, PaginationParams, DeleteResponse } from '@/types/common';
import type {
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
  UpdateTaskStatusRequest,
  TaskFilters,
} from '@/types/task';

export const getTasks = async (
  filters?: TaskFilters & PaginationParams,
): Promise<PaginatedResponse<Task>> => {
  const { data } = await apiClient.get<PaginatedResponse<Task>>('/tasks', {
    params: filters,
  });
  return data;
};

export const getTask = async (id: string): Promise<Task> => {
  const { data } = await apiClient.get<Task>(`/tasks/${id}`);
  return data;
};

export const createTask = async (body: CreateTaskRequest): Promise<Task> => {
  const { data } = await apiClient.post<Task>('/tasks', body);
  return data;
};

export const updateTask = async (
  id: string,
  body: UpdateTaskRequest,
): Promise<Task> => {
  const { data } = await apiClient.put<Task>(`/tasks/${id}`, body);
  return data;
};

export const updateTaskStatus = async (
  id: string,
  body: UpdateTaskStatusRequest,
): Promise<Task> => {
  const { data } = await apiClient.patch<Task>(`/tasks/${id}/status`, body);
  return data;
};

export const deleteTask = async (id: string): Promise<DeleteResponse> => {
  const { data } = await apiClient.delete<DeleteResponse>(`/tasks/${id}`);
  return data;
};
