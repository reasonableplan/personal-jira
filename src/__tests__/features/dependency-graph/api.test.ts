import { describe, it, expect, vi, beforeEach } from "vitest";
import { fetchDependencyGraph } from "../../../features/dependency-graph/api";
import { API_BASE_URL, ENDPOINTS } from "../../../features/dependency-graph/constants";

const MOCK_RESPONSE = {
  issues: [{ id: "1", title: "Test", status: "READY", priority: "LOW" }],
  dependencies: [],
};

describe("fetchDependencyGraph", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    global.fetch = vi.fn();
  });

  it("fetches all dependencies when no issueId provided", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(MOCK_RESPONSE),
    } as Response);

    const result = await fetchDependencyGraph();

    expect(fetch).toHaveBeenCalledWith(
      `${API_BASE_URL}${ENDPOINTS.DEPENDENCY_GRAPH}`,
    );
    expect(result).toEqual(MOCK_RESPONSE);
  });

  it("fetches dependencies for specific issue", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(MOCK_RESPONSE),
    } as Response);

    await fetchDependencyGraph("5");

    expect(fetch).toHaveBeenCalledWith(
      `${API_BASE_URL}${ENDPOINTS.DEPENDENCY_GRAPH}?issue_id=5`,
    );
  });

  it("throws on non-ok response", async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
    } as Response);

    await expect(fetchDependencyGraph()).rejects.toThrow(
      "Failed to fetch dependency graph: 500 Internal Server Error",
    );
  });
});
