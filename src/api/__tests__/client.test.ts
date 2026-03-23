import { ApiClient, ApiError } from '../client';
import type { IssueCreate, IssueUpdate, TransitionRequest, DependencyCreate } from '../../types/issue';

const BASE_URL = 'http://localhost:8000';

describe('ApiClient', () => {
  let client: ApiClient;
  let fetchMock: jest.SpyInstance;

  beforeEach(() => {
    client = new ApiClient(BASE_URL);
    fetchMock = jest.spyOn(globalThis, 'fetch');
  });

  afterEach(() => {
    fetchMock.mockRestore();
  });

  const mockResponse = (data: unknown, status = 200): Response =>
    ({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(data), text: () => Promise.resolve(JSON.stringify(data)) } as Response);

  describe('createIssue', () => {
    it('sends POST /api/v1/issues with body', async () => {
      const payload: IssueCreate = { title: 'Test Issue', priority: 'medium', issue_type: 'task' };
      const created = { id: 'uuid-1', ...payload, status: 'backlog', created_at: '2026-03-23T00:00:00Z', updated_at: '2026-03-23T00:00:00Z' };
      fetchMock.mockResolvedValueOnce(mockResponse(created, 201));

      const result = await client.createIssue(payload);

      expect(fetchMock).toHaveBeenCalledWith(`${BASE_URL}/api/v1/issues`, expect.objectContaining({ method: 'POST', body: JSON.stringify(payload) }));
      expect(result).toEqual(created);
    });

    it('throws ApiError on 422', async () => {
      fetchMock.mockResolvedValueOnce(mockResponse({ detail: 'Validation error' }, 422));

      await expect(client.createIssue({ title: '' } as IssueCreate)).rejects.toThrow(ApiError);
    });
  });

  describe('getIssue', () => {
    it('sends GET /api/v1/issues/:id', async () => {
      const issue = { id: 'uuid-1', title: 'Test', status: 'backlog', children: [], dependencies: [] };
      fetchMock.mockResolvedValueOnce(mockResponse(issue));

      const result = await client.getIssue('uuid-1');

      expect(fetchMock).toHaveBeenCalledWith(`${BASE_URL}/api/v1/issues/uuid-1`, expect.objectContaining({ method: 'GET' }));
      expect(result).toEqual(issue);
    });

    it('throws ApiError on 404', async () => {
      fetchMock.mockResolvedValueOnce(mockResponse({ detail: 'Not found' }, 404));

      await expect(client.getIssue('nonexistent')).rejects.toThrow(ApiError);
    });
  });

  describe('listIssues', () => {
    it('sends GET /api/v1/issues with pagination params', async () => {
      const response = { items: [], total: 0, offset: 0, limit: 20 };
      fetchMock.mockResolvedValueOnce(mockResponse(response));

      const result = await client.listIssues({ offset: 0, limit: 20 });

      expect(fetchMock).toHaveBeenCalledWith(`${BASE_URL}/api/v1/issues?offset=0&limit=20`, expect.objectContaining({ method: 'GET' }));
      expect(result).toEqual(response);
    });

    it('applies status and priority filters', async () => {
      const response = { items: [], total: 0, offset: 0, limit: 20 };
      fetchMock.mockResolvedValueOnce(mockResponse(response));

      await client.listIssues({ offset: 0, limit: 20, status: 'backlog', priority: 'high' });

      expect(fetchMock).toHaveBeenCalledWith(`${BASE_URL}/api/v1/issues?offset=0&limit=20&status=backlog&priority=high`, expect.objectContaining({ method: 'GET' }));
    });
  });

  describe('updateIssue', () => {
    it('sends PATCH /api/v1/issues/:id with partial body', async () => {
      const update: IssueUpdate = { title: 'Updated' };
      const updated = { id: 'uuid-1', title: 'Updated', status: 'backlog' };
      fetchMock.mockResolvedValueOnce(mockResponse(updated));

      const result = await client.updateIssue('uuid-1', update);

      expect(fetchMock).toHaveBeenCalledWith(`${BASE_URL}/api/v1/issues/uuid-1`, expect.objectContaining({ method: 'PATCH', body: JSON.stringify(update) }));
      expect(result).toEqual(updated);
    });
  });

  describe('deleteIssue', () => {
    it('sends DELETE /api/v1/issues/:id (soft delete)', async () => {
      fetchMock.mockResolvedValueOnce(mockResponse(null, 204));

      await client.deleteIssue('uuid-1');

      expect(fetchMock).toHaveBeenCalledWith(`${BASE_URL}/api/v1/issues/uuid-1`, expect.objectContaining({ method: 'DELETE' }));
    });

    it('sends DELETE with hard=true query param', async () => {
      fetchMock.mockResolvedValueOnce(mockResponse(null, 204));

      await client.deleteIssue('uuid-1', true);

      expect(fetchMock).toHaveBeenCalledWith(`${BASE_URL}/api/v1/issues/uuid-1?hard=true`, expect.objectContaining({ method: 'DELETE' }));
    });
  });

  describe('transitionIssue', () => {
    it('sends POST /api/v1/issues/:id/transition', async () => {
      const body: TransitionRequest = { status: 'ready' };
      const result = { id: 'uuid-1', status: 'ready' };
      fetchMock.mockResolvedValueOnce(mockResponse(result));

      const res = await client.transitionIssue('uuid-1', body);

      expect(fetchMock).toHaveBeenCalledWith(`${BASE_URL}/api/v1/issues/uuid-1/transition`, expect.objectContaining({ method: 'POST', body: JSON.stringify(body) }));
      expect(res).toEqual(result);
    });

    it('throws ApiError on invalid transition (422)', async () => {
      fetchMock.mockResolvedValueOnce(mockResponse({ detail: 'Invalid transition' }, 422));

      await expect(client.transitionIssue('uuid-1', { status: 'done' })).rejects.toThrow(ApiError);
    });
  });

  describe('dependencies', () => {
    it('addDependency sends POST', async () => {
      const dep: DependencyCreate = { blocked_by_issue_id: 'uuid-2' };
      fetchMock.mockResolvedValueOnce(mockResponse({ blocker_id: 'uuid-2', blocked_id: 'uuid-1' }, 201));

      await client.addDependency('uuid-1', dep);

      expect(fetchMock).toHaveBeenCalledWith(`${BASE_URL}/api/v1/issues/uuid-1/dependencies`, expect.objectContaining({ method: 'POST', body: JSON.stringify(dep) }));
    });

    it('getDependencies sends GET', async () => {
      fetchMock.mockResolvedValueOnce(mockResponse({ blocked_by: [], blocks: [] }));

      const result = await client.getDependencies('uuid-1');

      expect(fetchMock).toHaveBeenCalledWith(`${BASE_URL}/api/v1/issues/uuid-1/dependencies`, expect.objectContaining({ method: 'GET' }));
      expect(result).toEqual({ blocked_by: [], blocks: [] });
    });

    it('removeDependency sends DELETE', async () => {
      fetchMock.mockResolvedValueOnce(mockResponse(null, 204));

      await client.removeDependency('uuid-1', 'uuid-2');

      expect(fetchMock).toHaveBeenCalledWith(`${BASE_URL}/api/v1/issues/uuid-1/dependencies/uuid-2`, expect.objectContaining({ method: 'DELETE' }));
    });
  });

  describe('ApiError', () => {
    it('contains status and detail', async () => {
      fetchMock.mockResolvedValueOnce(mockResponse({ detail: 'Conflict: children exist' }, 409));

      try {
        await client.deleteIssue('uuid-1');
        fail('should have thrown');
      } catch (err) {
        expect(err).toBeInstanceOf(ApiError);
        expect((err as ApiError).status).toBe(409);
        expect((err as ApiError).detail).toBe('Conflict: children exist');
      }
    });
  });
});
