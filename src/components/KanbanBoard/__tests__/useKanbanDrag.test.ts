import { describe, it, expect } from "vitest";
import { reorderItems } from "../../../hooks/useKanbanDrag";
import { IssueType, IssueStatus, Priority } from "../../../types/issue";
import type { Issue } from "../../../types/issue";

function makeIssue(id: string, order: number): Issue {
  return {
    id,
    title: `Issue ${id}`,
    description: "",
    issue_type: IssueType.TASK,
    status: IssueStatus.READY,
    priority: Priority.MEDIUM,
    priority_order: order,
    parent_id: null,
    retry_count: 0,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  };
}

describe("reorderItems", () => {
  it("moves item forward", () => {
    const items = [makeIssue("a", 0), makeIssue("b", 1), makeIssue("c", 2)];
    const result = reorderItems(items, "a", "c");
    expect(result.map((i) => i.id)).toEqual(["b", "c", "a"]);
  });

  it("moves item backward", () => {
    const items = [makeIssue("a", 0), makeIssue("b", 1), makeIssue("c", 2)];
    const result = reorderItems(items, "c", "a");
    expect(result.map((i) => i.id)).toEqual(["c", "a", "b"]);
  });

  it("updates priority_order after reorder", () => {
    const items = [makeIssue("a", 0), makeIssue("b", 1), makeIssue("c", 2)];
    const result = reorderItems(items, "a", "c");
    expect(result.map((i) => i.priority_order)).toEqual([0, 1, 2]);
  });

  it("returns same array for invalid fromId", () => {
    const items = [makeIssue("a", 0), makeIssue("b", 1)];
    const result = reorderItems(items, "x", "b");
    expect(result).toBe(items);
  });

  it("returns same array for invalid toId", () => {
    const items = [makeIssue("a", 0), makeIssue("b", 1)];
    const result = reorderItems(items, "a", "x");
    expect(result).toBe(items);
  });

  it("handles single item", () => {
    const items = [makeIssue("a", 0)];
    const result = reorderItems(items, "a", "a");
    expect(result.map((i) => i.id)).toEqual(["a"]);
  });
});
