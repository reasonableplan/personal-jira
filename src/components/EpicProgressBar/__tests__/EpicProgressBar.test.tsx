import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { EpicProgressBar } from "../EpicProgressBar";
import type { EpicProgress } from "../../../types/issue";

function makeProgress(overrides: Partial<EpicProgress> = {}): EpicProgress {
  return { total: 10, done: 3, in_progress: 2, percentage: 30, ...overrides };
}

describe("EpicProgressBar", () => {
  it("renders percentage text", () => {
    render(<EpicProgressBar progress={makeProgress()} />);
    expect(screen.getByText("30%")).toBeInTheDocument();
  });

  it("renders count summary", () => {
    render(<EpicProgressBar progress={makeProgress()} />);
    expect(screen.getByText("3 / 10 done")).toBeInTheDocument();
  });

  it("renders done segment with correct width", () => {
    render(<EpicProgressBar progress={makeProgress()} />);
    const done = screen.getByTestId("progress-done");
    expect(done).toHaveStyle({ width: "30%" });
  });

  it("renders in-progress segment with correct width", () => {
    render(<EpicProgressBar progress={makeProgress()} />);
    const inProgress = screen.getByTestId("progress-in-progress");
    expect(inProgress).toHaveStyle({ width: "20%" });
  });

  it("shows 0% for empty epic", () => {
    render(
      <EpicProgressBar
        progress={{ total: 0, done: 0, in_progress: 0, percentage: 0 }}
      />,
    );
    expect(screen.getByText("0%")).toBeInTheDocument();
    expect(screen.getByText("0 / 0 done")).toBeInTheDocument();
  });

  it("shows 100% when all done", () => {
    render(
      <EpicProgressBar
        progress={{ total: 5, done: 5, in_progress: 0, percentage: 100 }}
      />,
    );
    expect(screen.getByText("100%")).toBeInTheDocument();
    const done = screen.getByTestId("progress-done");
    expect(done).toHaveStyle({ width: "100%" });
  });

  it("applies custom className", () => {
    const { container } = render(
      <EpicProgressBar progress={makeProgress()} className="custom" />,
    );
    expect(container.firstChild).toHaveClass("custom");
  });

  it("renders loading skeleton when loading", () => {
    render(<EpicProgressBar progress={makeProgress()} loading />);
    expect(screen.getByTestId("progress-skeleton")).toBeInTheDocument();
  });
});
