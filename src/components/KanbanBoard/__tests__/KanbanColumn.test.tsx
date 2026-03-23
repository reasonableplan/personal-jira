import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { KanbanColumn } from "../KanbanColumn";
import { IssueType, IssueStatus, Priority } from "../../../types/issue";
import type { Issue } from "../../../types/issue";

const ISSUES: Issue[] = [
  {
    id: "a",
    title: "Task A",
    description: "",
    issue_type: IssueType.TASK,
    status: IssueStatus.READY,
    priority: Priority.HIGH,
    priority_order: 0,
    parent_id: null,
    retry_count: 0,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
  {
    id: "b",
    title: "Task B",
    description: "",
    issue_type: IssueType.TASK,
    status: IssueStatus.READY,
    priority: Priority.LOW,
    priority_order: 1,
    parent_id: null,
    retry_count: 0,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

describe("KanbanColumn", () => {
  it("renders column title", () => {
    render(
      <KanbanColumn
        status={IssueStatus.READY}
        issues={ISSUES}
        dragState={{ draggedId: null, overId: null }}
        onDragStart={vi.fn()}
        onDragOver={vi.fn()}
        onDrop={vi.fn()}
        onDragEnd={vi.fn()}
      />,
    );
    expect(screen.getByText("Ready")).toBeInTheDocument();
  });

  it("renders issue count", () => {
    render(
      <KanbanColumn
        status={IssueStatus.READY}
        issues={ISSUES}
        dragState={{ draggedId: null, overId: null }}
        onDragStart={vi.fn()}
        onDragOver={vi.fn()}
        onDrop={vi.fn()}
        onDragEnd={vi.fn()}
      />,
    );
    expect(screen.getByText("2")).toBeInTheDocument();
  });

  it("renders all cards", () => {
    render(
      <KanbanColumn
        status={IssueStatus.READY}
        issues={ISSUES}
        dragState={{ draggedId: null, overId: null }}
        onDragStart={vi.fn()}
        onDragOver={vi.fn()}
        onDrop={vi.fn()}
        onDragEnd={vi.fn()}
      />,
    );
    expect(screen.getByText("Task A")).toBeInTheDocument();
    expect(screen.getByText("Task B")).toBeInTheDocument();
  });

  it("calls onDrop on drop event", () => {
    const onDrop = vi.fn();
    render(
      <KanbanColumn
        status={IssueStatus.READY}
        issues={ISSUES}
        dragState={{ draggedId: "a", overId: "b" }}
        onDragStart={vi.fn()}
        onDragOver={vi.fn()}
        onDrop={onDrop}
        onDragEnd={vi.fn()}
      />,
    );
    fireEvent.drop(screen.getByTestId("kanban-column-ready"));
    expect(onDrop).toHaveBeenCalled();
  });

  it("sorts issues by priority_order", () => {
    const reversed = [...ISSUES].reverse();
    render(
      <KanbanColumn
        status={IssueStatus.READY}
        issues={reversed}
        dragState={{ draggedId: null, overId: null }}
        onDragStart={vi.fn()}
        onDragOver={vi.fn()}
        onDrop={vi.fn()}
        onDragEnd={vi.fn()}
      />,
    );
    const cards = screen.getAllByTestId(/^kanban-card-/);
    expect(cards[0]).toHaveTextContent("Task A");
    expect(cards[1]).toHaveTextContent("Task B");
  });
});
