import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { KanbanCard } from "../KanbanCard";
import { IssueType, IssueStatus, Priority } from "../../../types/issue";
import type { Issue } from "../../../types/issue";

const ISSUE: Issue = {
  id: "issue-1",
  title: "Fix login bug",
  description: "Users cannot login",
  issue_type: IssueType.BUG,
  status: IssueStatus.IN_PROGRESS,
  priority: Priority.HIGH,
  priority_order: 0,
  parent_id: null,
  retry_count: 0,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

describe("KanbanCard", () => {
  it("renders issue title", () => {
    render(<KanbanCard issue={ISSUE} onDragStart={vi.fn()} onDragOver={vi.fn()} />);
    expect(screen.getByText("Fix login bug")).toBeInTheDocument();
  });

  it("renders issue type badge", () => {
    render(<KanbanCard issue={ISSUE} onDragStart={vi.fn()} onDragOver={vi.fn()} />);
    expect(screen.getByText("bug")).toBeInTheDocument();
  });

  it("renders priority badge", () => {
    render(<KanbanCard issue={ISSUE} onDragStart={vi.fn()} onDragOver={vi.fn()} />);
    expect(screen.getByText("high")).toBeInTheDocument();
  });

  it("calls onDragStart on drag", () => {
    const onDragStart = vi.fn();
    render(<KanbanCard issue={ISSUE} onDragStart={onDragStart} onDragOver={vi.fn()} />);
    fireEvent.dragStart(screen.getByTestId("kanban-card-issue-1"));
    expect(onDragStart).toHaveBeenCalledWith("issue-1");
  });

  it("calls onDragOver on dragover", () => {
    const onDragOver = vi.fn();
    render(<KanbanCard issue={ISSUE} onDragStart={vi.fn()} onDragOver={onDragOver} />);
    fireEvent.dragOver(screen.getByTestId("kanban-card-issue-1"));
    expect(onDragOver).toHaveBeenCalledWith("issue-1");
  });

  it("applies dragging class when isDragging", () => {
    render(<KanbanCard issue={ISSUE} onDragStart={vi.fn()} onDragOver={vi.fn()} isDragging />);
    expect(screen.getByTestId("kanban-card-issue-1")).toHaveClass("dragging");
  });

  it("applies dragOver class when isDragOver", () => {
    render(<KanbanCard issue={ISSUE} onDragStart={vi.fn()} onDragOver={vi.fn()} isDragOver />);
    expect(screen.getByTestId("kanban-card-issue-1")).toHaveClass("dragOver");
  });
});
