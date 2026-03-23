import { SearchResult } from '../types/issue';
import { API_BASE_URL } from '../constants/api';

export async function searchIssues(
  query: string,
  signal?: AbortSignal
): Promise<SearchResult[]> {
  const url = `${API_BASE_URL}/api/v1/issues/search?q=${encodeURIComponent(query)}`;
  const response = await fetch(url, { signal });

  if (!response.ok) {
    throw new Error(`Search failed: ${response.status}`);
  }

  return response.json();
}
