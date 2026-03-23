import type { DashboardStats, Issue } from '../types/issue';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) {
    throw new ApiError(res.status, `API error: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  getDashboardStats: () => fetchJson<DashboardStats>('/dashboard/stats'),
  getIssues: () => fetchJson<Issue[]>('/issues'),
  getIssue: (id: string) => fetchJson<Issue>(`/issues/${id}`),
};
