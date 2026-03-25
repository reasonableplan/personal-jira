import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppLayout } from "@/components/AppLayout";

function renderWithProviders(initialEntry = "/board") {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[initialEntry]}>
        <AppLayout />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("AppLayout", () => {
  it("renders sidebar with Board link", () => {
    renderWithProviders();
    expect(screen.getByText("Board")).toBeInTheDocument();
  });

  it("renders sidebar with Epics link", () => {
    renderWithProviders();
    expect(screen.getByText("Epics")).toBeInTheDocument();
  });

  it("renders sidebar with Labels link", () => {
    renderWithProviders();
    expect(screen.getByText("Labels")).toBeInTheDocument();
  });

  it("renders an outlet for child routes", () => {
    renderWithProviders();
    expect(document.querySelector("main")).toBeInTheDocument();
  });
});
