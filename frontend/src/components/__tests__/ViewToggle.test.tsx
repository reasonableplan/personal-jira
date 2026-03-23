import { render, screen, fireEvent } from "@testing-library/react";
import { ViewToggle } from "../ViewToggle";
import { VIEW_TYPES } from "../../types/view";
import type { ViewType } from "../../types/view";

describe("ViewToggle", () => {
  const defaultProps = {
    view: VIEW_TYPES.BOARD as ViewType,
    onToggle: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders board and table buttons", () => {
    render(<ViewToggle {...defaultProps} />);
    expect(screen.getByRole("button", { name: /board/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /table/i })).toBeInTheDocument();
  });

  it("marks board button as active when view is board", () => {
    render(<ViewToggle {...defaultProps} view={VIEW_TYPES.BOARD} />);
    const boardBtn = screen.getByRole("button", { name: /board/i });
    expect(boardBtn).toHaveAttribute("aria-pressed", "true");
    const tableBtn = screen.getByRole("button", { name: /table/i });
    expect(tableBtn).toHaveAttribute("aria-pressed", "false");
  });

  it("marks table button as active when view is table", () => {
    render(<ViewToggle {...defaultProps} view={VIEW_TYPES.TABLE} />);
    const tableBtn = screen.getByRole("button", { name: /table/i });
    expect(tableBtn).toHaveAttribute("aria-pressed", "true");
    const boardBtn = screen.getByRole("button", { name: /board/i });
    expect(boardBtn).toHaveAttribute("aria-pressed", "false");
  });

  it("calls onToggle when inactive button is clicked", () => {
    render(<ViewToggle {...defaultProps} view={VIEW_TYPES.BOARD} />);
    fireEvent.click(screen.getByRole("button", { name: /table/i }));
    expect(defaultProps.onToggle).toHaveBeenCalledWith(VIEW_TYPES.TABLE);
  });

  it("does not call onToggle when active button is clicked", () => {
    render(<ViewToggle {...defaultProps} view={VIEW_TYPES.BOARD} />);
    fireEvent.click(screen.getByRole("button", { name: /board/i }));
    expect(defaultProps.onToggle).not.toHaveBeenCalled();
  });

  it("renders with correct aria role", () => {
    render(<ViewToggle {...defaultProps} />);
    expect(screen.getByRole("group")).toBeInTheDocument();
  });

  it("applies active class to current view button", () => {
    render(<ViewToggle {...defaultProps} view={VIEW_TYPES.TABLE} />);
    const tableBtn = screen.getByRole("button", { name: /table/i });
    expect(tableBtn.className).toContain("active");
    const boardBtn = screen.getByRole("button", { name: /board/i });
    expect(boardBtn.className).not.toContain("active");
  });
});
