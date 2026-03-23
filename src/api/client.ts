import type { Issue, Comment, CreateIssueRequest, CreateCommentRequest } from '@/types/issue';
import type { IssueStatus } from '@/types/issue';

const API_BASE = '/api/v1';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail ?? `HTTP ${response.status}`);
  }
  return response.json();
}

export const api = {
  getIssues: (): Promise<Issue[]> => request('/issues'),

  createIssue: (data: CreateIssueRequest): Promise<Issue> =>
    request('/issues', { method: 'POST', body: JSON.stringify(data) }),

  getIssue: (id: string): Promise<Issue> => request(`/issues/${id}`),

  transitionIssue: (id: string, status: IssueStatus): Promise<Issue> =>
    request(`/issues/${id}/transition`, {
      method: 'POST',
      body: JSON.stringify({ status }),
    }),

  getComments: (issueId: string): Promise<Comment[]> =>
    request(`/issues/${issueId}/comments`),

  createComment: (issueId: string, data: CreateCommentRequest): Promise<Comment> =>
    request(`/issues/${issueId}/comments`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};
