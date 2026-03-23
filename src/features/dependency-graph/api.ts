import type { DependencyGraphData } from "./types";
import { API_BASE_URL, ENDPOINTS } from "./constants";

export async function fetchDependencyGraph(
  issueId?: string,
): Promise<DependencyGraphData> {
  const url = issueId
    ? `${API_BASE_URL}${ENDPOINTS.DEPENDENCY_GRAPH}?issue_id=${issueId}`
    : `${API_BASE_URL}${ENDPOINTS.DEPENDENCY_GRAPH}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(
      `Failed to fetch dependency graph: ${response.status} ${response.statusText}`,
    );
  }

  return response.json();
}
