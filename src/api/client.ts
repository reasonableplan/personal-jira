import type { Issue, IssueCreate, IssueUpdate, IssueListParams, IssueListResponse, IssueDetailResponse, IssueDependency, DependencyResponse, TransitionRequest, DependencyCreate } from '../types/issue';

const API_PREFIX = '/api/v1';
const DEFAULT_HEADERS: HeadersInit = { 'Content-Type': 'application/json' };

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: string,
  ) {
    super(`API Error ${status}: ${detail}`);
    this.name = 'ApiError';
  }
}

export class ApiClient {
  private readonly baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const response = await fetch(url, { ...options, headers: { ...DEFAULT_HEADERS, ...options.headers } });

    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try {
        const body = await response.json();
        detail = body.detail ?? JSON.stringify(body);
      } catch {
        detail = await response.text().catch(() => detail);
      }
      throw new ApiError(response.status, detail);
    }

    if (response.status === 204) return null as T;
    return response.json() as Promise<T>;
  }

  async createIssue(data: IssueCreate): Promise<Issue> {
    return this.request<Issue>(`${API_PREFIX}/issues`, { method: 'POST', body: JSON.stringify(data) });
  }

  async getIssue(id: string): Promise<IssueDetailResponse> {
    return this.request<IssueDetailResponse>(`${API_PREFIX}/issues/${id}`, { method: 'GET' });
  }

  async listIssues(params: IssueListParams): Promise<IssueListResponse> {
    const query = new URLSearchParams();
    query.set('offset', String(params.offset));
    query.set('limit', String(params.limit));
    if (params.status) query.set('status', params.status);
    if (params.priority) query.set('priority', params.priority);
    if (params.issue_type) query.set('issue_type', params.issue_type);
    if (params.parent_id) query.set('parent_id', params.parent_id);
    return this.request<IssueListResponse>(`${API_PREFIX}/issues?${query.toString()}`, { method: 'GET' });
  }

  async updateIssue(id: string, data: IssueUpdate): Promise<Issue> {
    return this.request<Issue>(`${API_PREFIX}/issues/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
  }

  async deleteIssue(id: string, hard = false): Promise<void> {
    const query = hard ? '?hard=true' : '';
    return this.request<void>(`${API_PREFIX}/issues/${id}${query}`, { method: 'DELETE' });
  }

  async transitionIssue(id: string, data: TransitionRequest): Promise<Issue> {
    return this.request<Issue>(`${API_PREFIX}/issues/${id}/transition`, { method: 'POST', body: JSON.stringify(data) });
  }

  async addDependency(issueId: string, data: DependencyCreate): Promise<IssueDependency> {
    return this.request<IssueDependency>(`${API_PREFIX}/issues/${issueId}/dependencies`, { method: 'POST', body: JSON.stringify(data) });
  }

  async getDependencies(issueId: string): Promise<DependencyResponse> {
    return this.request<DependencyResponse>(`${API_PREFIX}/issues/${issueId}/dependencies`, { method: 'GET' });
  }

  async removeDependency(issueId: string, blockerIssueId: string): Promise<void> {
    return this.request<void>(`${API_PREFIX}/issues/${issueId}/dependencies/${blockerIssueId}`, { method: 'DELETE' });
  }
}
