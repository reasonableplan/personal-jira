import { apiClient } from '@/api/client';
import type { PaginatedResponse, PaginationParams, DeleteResponse } from '@/types/common';
import type { Label } from '@/types/label';

export interface CreateLabelRequest {
  name: string;
  color: string;
}

export interface UpdateLabelRequest {
  name?: string;
  color?: string;
}

export const getLabels = async (
  params?: PaginationParams,
): Promise<PaginatedResponse<Label>> => {
  const { data } = await apiClient.get<PaginatedResponse<Label>>('/labels', {
    params,
  });
  return data;
};

export const createLabel = async (
  body: CreateLabelRequest,
): Promise<Label> => {
  const { data } = await apiClient.post<Label>('/labels', body);
  return data;
};

export const updateLabel = async (
  id: string,
  body: UpdateLabelRequest,
): Promise<Label> => {
  const { data } = await apiClient.put<Label>(`/labels/${id}`, body);
  return data;
};

export const deleteLabel = async (id: string): Promise<DeleteResponse> => {
  const { data } = await apiClient.delete<DeleteResponse>(`/labels/${id}`);
  return data;
};
