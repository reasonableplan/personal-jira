import { apiClient } from '@/api/client';
import type { PaginatedResponse, PaginationParams, DeleteResponse } from '@/types/common';
import type { Epic, CreateEpicRequest, UpdateEpicRequest } from '@/types/epic';

export const getEpics = async (
  params?: PaginationParams,
): Promise<PaginatedResponse<Epic>> => {
  const { data } = await apiClient.get<PaginatedResponse<Epic>>('/epics', {
    params,
  });
  return data;
};

export const getEpic = async (id: string): Promise<Epic> => {
  const { data } = await apiClient.get<Epic>(`/epics/${id}`);
  return data;
};

export const createEpic = async (body: CreateEpicRequest): Promise<Epic> => {
  const { data } = await apiClient.post<Epic>('/epics', body);
  return data;
};

export const updateEpic = async (
  id: string,
  body: UpdateEpicRequest,
): Promise<Epic> => {
  const { data } = await apiClient.put<Epic>(`/epics/${id}`, body);
  return data;
};

export const deleteEpic = async (id: string): Promise<DeleteResponse> => {
  const { data } = await apiClient.delete<DeleteResponse>(`/epics/${id}`);
  return data;
};
