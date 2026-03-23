import type { Issue, IssueCreate, IssueStatus } from '@/types/issue';

const API_BASE = '/api/v1';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API error ${response.status}: ${errorBody}`);
  }

  return response.json() as Promise<T>;
}

export const issueApi = {
  list(): Promise<Issue[]> {
    return request<Issue[]>('/issues');
  },

  get(id: string): Promise<Issue> {
    return request<Issue>(`/issues/${id}`);
  },

  create(data: IssueCreate): Promise<Issue> {
    return request<Issue>('/issues', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  transition(id: string, status: IssueStatus): Promise<Issue> {
    return request<Issue>(`/issues/${id}/transition`, {
      method: 'POST',
      body: JSON.stringify({ status }),
    });
  },
};
