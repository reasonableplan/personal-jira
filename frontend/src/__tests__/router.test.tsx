import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "@/App";

function renderApp(initialEntry = "/") {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[initialEntry]}>
        <App />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("Router", () => {
  it("/ redirects to /board", () => {
    renderApp("/");
    expect(screen.getByText("Board")).toBeInTheDocument();
  });

  it("/board renders board page", () => {
    renderApp("/board");
    expect(screen.getByText("Board")).toBeInTheDocument();
  });

  it("/epics/:id renders epic detail page", () => {
    renderApp("/epics/123");
    expect(screen.getByText("Epic Detail")).toBeInTheDocument();
  });

  it("/stories/:id renders story detail page", () => {
    renderApp("/stories/123");
    expect(screen.getByText("Story Detail")).toBeInTheDocument();
  });

  it("/tasks/:id renders task detail page", () => {
    renderApp("/tasks/123");
    expect(screen.getByText("Task Detail")).toBeInTheDocument();
  });

  it("/settings/labels renders labels page", () => {
    renderApp("/settings/labels");
    expect(screen.getByText("Labels")).toBeInTheDocument();
  });
});
