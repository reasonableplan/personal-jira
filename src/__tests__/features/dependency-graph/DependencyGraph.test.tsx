import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { ReactFlowProvider } from "@xyflow/react";
import { DependencyGraph } from "../../../features/dependency-graph/DependencyGraph";
import * as api from "../../../features/dependency-graph/api";
import type { DependencyGraphData } from "../../../features/dependency-graph/types";

vi.mock("../../../features/dependency-graph/api");

const MOCK_GRAPH: DependencyGraphData = {
  issues: [
    { id: "1", title: "Auth 구현", status: "IN_PROGRESS", priority: "HIGH" },
    { id: "2", title: "DB 스키마", status: "DONE", priority: "MEDIUM" },
    { id: "3", title: "API 설계", status: "READY", priority: "HIGH" },
  ],
  dependencies: [
    { from_issue_id: "1", to_issue_id: "2", type: "BLOCKED_BY" },
    { from_issue_id: "3", to_issue_id: "2", type: "BLOCKED_BY" },
  ],
};

const renderGraph = (issueId?: string) =>
  render(
    <ReactFlowProvider>
      <DependencyGraph issueId={issueId} />
    </ReactFlowProvider>,
  );

describe("DependencyGraph", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it("renders loading state initially", () => {
    vi.mocked(api.fetchDependencyGraph).mockReturnValue(
      new Promise(() => {}),
    );
    renderGraph();
    expect(screen.getByTestId("dependency-graph-loading")).toBeInTheDocument();
  });

  it("renders graph nodes for each issue", async () => {
    vi.mocked(api.fetchDependencyGraph).mockResolvedValue(MOCK_GRAPH);
    renderGraph();
    await waitFor(() => {
      expect(screen.getByText("Auth 구현")).toBeInTheDocument();
      expect(screen.getByText("DB 스키마")).toBeInTheDocument();
      expect(screen.getByText("API 설계")).toBeInTheDocument();
    });
  });

  it("renders error state on fetch failure", async () => {
    vi.mocked(api.fetchDependencyGraph).mockRejectedValue(
      new Error("Network error"),
    );
    renderGraph();
    await waitFor(() => {
      expect(screen.getByTestId("dependency-graph-error")).toBeInTheDocument();
    });
  });

  it("renders empty state when no data", async () => {
    vi.mocked(api.fetchDependencyGraph).mockResolvedValue({
      issues: [],
      dependencies: [],
    });
    renderGraph();
    await waitFor(() => {
      expect(screen.getByTestId("dependency-graph-empty")).toBeInTheDocument();
    });
  });

  it("passes issueId to fetch function", () => {
    vi.mocked(api.fetchDependencyGraph).mockReturnValue(
      new Promise(() => {}),
    );
    renderGraph("42");
    expect(api.fetchDependencyGraph).toHaveBeenCalledWith("42");
  });
});
