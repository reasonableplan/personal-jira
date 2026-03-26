import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { GlobalLoadingIndicator } from '@/components/common/GlobalLoadingIndicator';

vi.mock('@tanstack/react-query', async () => {
  const actual =
    await vi.importActual<typeof import('@tanstack/react-query')>(
      '@tanstack/react-query',
    );
  return {
    ...actual,
    useIsFetching: vi.fn(),
  };
});

import { useIsFetching } from '@tanstack/react-query';

const mockUseIsFetching = vi.mocked(useIsFetching);

function renderWithQueryClient(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>,
  );
}

describe('GlobalLoadingIndicator', () => {
  it('does not render when no queries are fetching', () => {
    mockUseIsFetching.mockReturnValue(0);
    renderWithQueryClient(<GlobalLoadingIndicator />);

    expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
  });

  it('renders loading bar when queries are fetching', () => {
    mockUseIsFetching.mockReturnValue(2);
    renderWithQueryClient(<GlobalLoadingIndicator />);

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
    expect(screen.getByLabelText('데이터 로딩 중')).toBeInTheDocument();
  });
});
