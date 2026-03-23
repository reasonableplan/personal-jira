import { describe, it, expect } from "vitest";
import { computeProgress } from "../../../hooks/useEpicProgress";
import { IssueType, IssueStatus, Priority } from "../../../types/issue";
import type { Issue } from "../../../types/issue";

function makeChild(status: IssueStatus): Issue {
  return {
    id: crypto.randomUUID(),
    title: "child",
    description: "",
    issue_type: IssueType.TASK,
    status,
    priority: Priority.MEDIUM,
    priority_order: 0,
    parent_id: "epic-1",
    retry_count: 0,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  };
}

describe("computeProgress", () => {
  it("returns zero for empty children", () => {
    const result = computeProgress([]);
    expect(result).toEqual({ total: 0, done: 0, in_progress: 0, percentage: 0 });
  });

  it("counts done children", () => {
    const children = [
      makeChild(IssueStatus.DONE),
      makeChild(IssueStatus.DONE),
      makeChild(IssueStatus.READY),
    ];
    const result = computeProgress(children);
    expect(result.done).toBe(2);
    expect(result.total).toBe(3);
    expect(result.percentage).toBe(67);
  });

  it("counts in_progress children", () => {
    const children = [
      makeChild(IssueStatus.IN_PROGRESS),
      makeChild(IssueStatus.IN_REVIEW),
      makeChild(IssueStatus.BACKLOG),
    ];
    const result = computeProgress(children);
    expect(result.in_progress).toBe(2);
    expect(result.done).toBe(0);
  });

  it("returns 100% when all done", () => {
    const children = [
      makeChild(IssueStatus.DONE),
      makeChild(IssueStatus.DONE),
    ];
    const result = computeProgress(children);
    expect(result.percentage).toBe(100);
  });

  it("does not count blocked/abandoned as in_progress", () => {
    const children = [
      makeChild(IssueStatus.BLOCKED),
      makeChild(IssueStatus.ABANDONED),
    ];
    const result = computeProgress(children);
    expect(result.in_progress).toBe(0);
    expect(result.done).toBe(0);
  });
});
