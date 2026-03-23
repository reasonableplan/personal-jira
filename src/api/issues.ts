import { Issue, IssueFilters, PaginatedResponse } from '../types/issue';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

export async function fetchIssues(
  page: number,
  pageSize: number,
  filters: IssueFilters = {},
  sortField?: string,
  sortOrder?: 'asc' | 'desc'
): Promise<PaginatedResponse<Issue>> {
  const params = new URLSearchParams();
  params.set('page', String(page));
  params.set('page_size', String(pageSize));

  if (filters.status) params.set('status', filters.status);
  if (filters.priority) params.set('priority', filters.priority);
  if (filters.issue_type) params.set('issue_type', filters.issue_type);
  if (filters.assignee) params.set('assignee', filters.assignee);
  if (filters.search) params.set('search', filters.search);
  if (sortField) params.set('sort_by', sortField);
  if (sortOrder) params.set('sort_order', sortOrder);

  const response = await fetch(`${API_BASE_URL}/issues?${params.toString()}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch issues: ${response.status} ${response.statusText}`);
  }

  return response.json();
}
