import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { fetchIssues } from '../../src/api/issues';
import { IssueStatus, IssuePriority, IssueType } from '../../src/types/issue';

const mockFetch = vi.fn();

beforeEach(() => {
  vi.stubGlobal('fetch', mockFetch);
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('fetchIssues', () => {
  it('fetches with page and page_size params', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ items: [], total: 0, page: 1, page_size: 20, total_pages: 0 }),
    });

    await fetchIssues(1, 20);

    const url = new URL(mockFetch.mock.calls[0][0], 'http://localhost');
    expect(url.searchParams.get('page')).toBe('1');
    expect(url.searchParams.get('page_size')).toBe('20');
  });

  it('includes filter params when provided', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ items: [], total: 0, page: 1, page_size: 20, total_pages: 0 }),
    });

    await fetchIssues(1, 20, {
      status: IssueStatus.IN_PROGRESS,
      priority: IssuePriority.HIGH,
      issue_type: IssueType.BUG,
      assignee: 'agent-1',
      search: 'login',
    });

    const url = new URL(mockFetch.mock.calls[0][0], 'http://localhost');
    expect(url.searchParams.get('status')).toBe('in_progress');
    expect(url.searchParams.get('priority')).toBe('high');
    expect(url.searchParams.get('issue_type')).toBe('bug');
    expect(url.searchParams.get('assignee')).toBe('agent-1');
    expect(url.searchParams.get('search')).toBe('login');
  });

  it('includes sort params when provided', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ items: [], total: 0, page: 1, page_size: 20, total_pages: 0 }),
    });

    await fetchIssues(1, 20, {}, 'priority', 'desc');

    const url = new URL(mockFetch.mock.calls[0][0], 'http://localhost');
    expect(url.searchParams.get('sort_by')).toBe('priority');
    expect(url.searchParams.get('sort_order')).toBe('desc');
  });

  it('omits undefined filter params', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ items: [], total: 0, page: 1, page_size: 20, total_pages: 0 }),
    });

    await fetchIssues(1, 20, { status: IssueStatus.TODO });

    const url = new URL(mockFetch.mock.calls[0][0], 'http://localhost');
    expect(url.searchParams.has('priority')).toBe(false);
    expect(url.searchParams.has('assignee')).toBe(false);
  });

  it('throws on non-ok response', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
    });

    await expect(fetchIssues(1, 20)).rejects.toThrow('Failed to fetch issues: 500 Internal Server Error');
  });
});
