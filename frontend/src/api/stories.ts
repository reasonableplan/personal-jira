import { apiClient } from '@/api/client';
import type { PaginatedResponse, PaginationParams, DeleteResponse } from '@/types/common';
import type { Story, CreateStoryRequest, UpdateStoryRequest } from '@/types/story';

export const getStories = async (
  epicId: string,
  params?: PaginationParams,
): Promise<PaginatedResponse<Story>> => {
  const { data } = await apiClient.get<PaginatedResponse<Story>>(
    `/epics/${epicId}/stories`,
    { params },
  );
  return data;
};

export const getStory = async (id: string): Promise<Story> => {
  const { data } = await apiClient.get<Story>(`/stories/${id}`);
  return data;
};

export const createStory = async (body: CreateStoryRequest): Promise<Story> => {
  const { data } = await apiClient.post<Story>('/stories', body);
  return data;
};

export const updateStory = async (
  id: string,
  body: UpdateStoryRequest,
): Promise<Story> => {
  const { data } = await apiClient.put<Story>(`/stories/${id}`, body);
  return data;
};

export const deleteStory = async (id: string): Promise<DeleteResponse> => {
  const { data } = await apiClient.delete<DeleteResponse>(`/stories/${id}`);
  return data;
};
