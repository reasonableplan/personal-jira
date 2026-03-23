import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { IssueNode } from "../../../features/dependency-graph/IssueNode";
import type { IssueNodeData } from "../../../features/dependency-graph/types";
import { STATUS_COLORS } from "../../../features/dependency-graph/constants";

const BASE_DATA: IssueNodeData = {
  id: "1",
  title: "Auth 구현",
  status: "IN_PROGRESS",
  priority: "HIGH",
};

const renderNode = (data: Partial<IssueNodeData> = {}) =>
  render(<IssueNode data={{ ...BASE_DATA, ...data }} />);

describe("IssueNode", () => {
  it("renders issue title", () => {
    renderNode();
    expect(screen.getByText("Auth 구현")).toBeInTheDocument();
  });

  it("renders issue status badge", () => {
    renderNode();
    expect(screen.getByText("IN_PROGRESS")).toBeInTheDocument();
  });

  it("renders priority indicator", () => {
    renderNode({ priority: "CRITICAL" });
    expect(screen.getByText("CRITICAL")).toBeInTheDocument();
  });

  it("applies correct status color", () => {
    renderNode({ status: "DONE" });
    const badge = screen.getByTestId("status-badge");
    expect(badge).toHaveStyle({ backgroundColor: STATUS_COLORS.DONE });
  });

  it("renders issue id", () => {
    renderNode({ id: "42" });
    expect(screen.getByText("#42")).toBeInTheDocument();
  });
});
