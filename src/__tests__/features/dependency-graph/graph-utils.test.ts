import { describe, it, expect } from "vitest";
import { buildGraphElements } from "../../../features/dependency-graph/graph-utils";
import type { DependencyGraphData } from "../../../features/dependency-graph/types";
import { GRAPH_LAYOUT } from "../../../features/dependency-graph/constants";

const MOCK_DATA: DependencyGraphData = {
  issues: [
    { id: "1", title: "Task A", status: "READY", priority: "HIGH" },
    { id: "2", title: "Task B", status: "IN_PROGRESS", priority: "LOW" },
    { id: "3", title: "Task C", status: "DONE", priority: "MEDIUM" },
  ],
  dependencies: [
    { from_issue_id: "1", to_issue_id: "2", type: "BLOCKED_BY" },
    { from_issue_id: "2", to_issue_id: "3", type: "BLOCKED_BY" },
  ],
};

describe("buildGraphElements", () => {
  it("creates a node for each issue", () => {
    const { nodes } = buildGraphElements(MOCK_DATA);
    expect(nodes).toHaveLength(3);
    expect(nodes.map((n) => n.id)).toEqual(["1", "2", "3"]);
  });

  it("creates an edge for each dependency", () => {
    const { edges } = buildGraphElements(MOCK_DATA);
    expect(edges).toHaveLength(2);
    expect(edges[0]).toMatchObject({ source: "1", target: "2" });
    expect(edges[1]).toMatchObject({ source: "2", target: "3" });
  });

  it("sets node type to issueNode", () => {
    const { nodes } = buildGraphElements(MOCK_DATA);
    nodes.forEach((node) => {
      expect(node.type).toBe("issueNode");
    });
  });

  it("assigns layout positions to nodes", () => {
    const { nodes } = buildGraphElements(MOCK_DATA);
    nodes.forEach((node) => {
      expect(node.position).toBeDefined();
      expect(typeof node.position.x).toBe("number");
      expect(typeof node.position.y).toBe("number");
    });
  });

  it("uses animated edges for BLOCKED_BY type", () => {
    const { edges } = buildGraphElements(MOCK_DATA);
    edges.forEach((edge) => {
      expect(edge.animated).toBe(true);
    });
  });

  it("spaces nodes using GRAPH_LAYOUT constants", () => {
    const { nodes } = buildGraphElements(MOCK_DATA);
    const xValues = nodes.map((n) => n.position.x);
    const yValues = nodes.map((n) => n.position.y);
    const xGaps = new Set(xValues);
    const yGaps = new Set(yValues);
    expect(xGaps.size).toBeGreaterThanOrEqual(1);
    expect(yGaps.size).toBeGreaterThanOrEqual(1);
  });

  it("returns empty arrays for empty data", () => {
    const { nodes, edges } = buildGraphElements({
      issues: [],
      dependencies: [],
    });
    expect(nodes).toEqual([]);
    expect(edges).toEqual([]);
  });

  it("highlights focused issue node", () => {
    const { nodes } = buildGraphElements(MOCK_DATA, "2");
    const focused = nodes.find((n) => n.id === "2");
    expect(focused?.data.isFocused).toBe(true);
    const other = nodes.find((n) => n.id === "1");
    expect(other?.data.isFocused).toBe(false);
  });
});
