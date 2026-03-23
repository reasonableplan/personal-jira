import type { Issue, ReorderRequest } from "../types/issue";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "Unknown error");
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export function fetchIssues(): Promise<Issue[]> {
  return request<Issue[]>("/issues");
}

export function fetchIssue(id: string): Promise<Issue> {
  return request<Issue>(`/issues/${id}`);
}

export function fetchEpicChildren(epicId: string): Promise<Issue[]> {
  return request<Issue[]>(`/issues/${epicId}/children`);
}

export function reorderPriority(issueId: string, newOrder: number): Promise<Issue> {
  return request<Issue>(`/issues/${issueId}/reorder`, {
    method: "PATCH",
    body: JSON.stringify({ new_order: newOrder } satisfies Omit<ReorderRequest, "issue_id">),
  });
}

export function batchReorder(requests: ReorderRequest[]): Promise<Issue[]> {
  return request<Issue[]>("/issues/reorder", {
    method: "PUT",
    body: JSON.stringify(requests),
  });
}
