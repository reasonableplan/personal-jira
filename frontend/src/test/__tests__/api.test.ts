import { describe, it, expect, vi, beforeEach } from 'vitest';
import { issueApi } from '@/services/api';
import type { Issue } from '@/types/issue';

const MOCK_ISSUE: Issue = {
  id: 'issue-1',
  title: 'Test Issue',
  description: null,
  status: 'Backlog',
  priority: 'Medium',
  parent_id: null,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('issueApi', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('list() fetches GET /api/v1/issues', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([MOCK_ISSUE]),
    });
    vi.stubGlobal('fetch', mockFetch);

    const result = await issueApi.list();

    expect(mockFetch).toHaveBeenCalledWith('/api/v1/issues', {
      headers: { 'Content-Type': 'application/json' },
    });
    expect(result).toEqual([MOCK_ISSUE]);
  });

  it('get() fetches GET /api/v1/issues/:id', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(MOCK_ISSUE),
    });
    vi.stubGlobal('fetch', mockFetch);

    const result = await issueApi.get('issue-1');

    expect(mockFetch).toHaveBeenCalledWith('/api/v1/issues/issue-1', {
      headers: { 'Content-Type': 'application/json' },
    });
    expect(result).toEqual(MOCK_ISSUE);
  });

  it('create() posts to /api/v1/issues', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(MOCK_ISSUE),
    });
    vi.stubGlobal('fetch', mockFetch);

    const result = await issueApi.create({ title: 'Test Issue' });

    expect(mockFetch).toHaveBeenCalledWith('/api/v1/issues', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: 'Test Issue' }),
    });
    expect(result).toEqual(MOCK_ISSUE);
  });

  it('transition() posts to /api/v1/issues/:id/transition', async () => {
    const moved = { ...MOCK_ISSUE, status: 'Ready' as const };
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(moved),
    });
    vi.stubGlobal('fetch', mockFetch);

    const result = await issueApi.transition('issue-1', 'Ready');

    expect(mockFetch).toHaveBeenCalledWith('/api/v1/issues/issue-1/transition', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'Ready' }),
    });
    expect(result).toEqual(moved);
  });

  it('throws on non-ok response', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 422,
      text: () => Promise.resolve('Invalid transition'),
    });
    vi.stubGlobal('fetch', mockFetch);

    await expect(issueApi.transition('issue-1', 'Done')).rejects.toThrow(
      'API error 422: Invalid transition',
    );
  });
});
