import { searchIssues } from '../../services/issueApi';
import { API_BASE_URL } from '../../constants/api';

global.fetch = jest.fn();
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;

const MOCK_RESPONSE = [
  { id: '1', title: 'Fix login bug', labels: ['bug', 'auth'] },
  { id: '2', title: 'Fix logout', labels: ['bug'] },
];

describe('searchIssues', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it('calls the correct endpoint with query param', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => MOCK_RESPONSE,
    } as Response);

    await searchIssues('Fix');

    expect(mockFetch).toHaveBeenCalledWith(
      `${API_BASE_URL}/api/v1/issues/search?q=${encodeURIComponent('Fix')}`,
      expect.objectContaining({ signal: expect.any(AbortSignal) })
    );
  });

  it('returns parsed results', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => MOCK_RESPONSE,
    } as Response);

    const results = await searchIssues('Fix');
    expect(results).toEqual(MOCK_RESPONSE);
  });

  it('throws on non-ok response', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
    } as Response);

    await expect(searchIssues('Fix')).rejects.toThrow('Search failed: 500');
  });

  it('supports abort signal', async () => {
    const controller = new AbortController();
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => MOCK_RESPONSE,
    } as Response);

    await searchIssues('Fix', controller.signal);

    expect(mockFetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({ signal: controller.signal })
    );
  });
});
