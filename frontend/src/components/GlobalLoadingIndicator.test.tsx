import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { GlobalLoadingIndicator } from './GlobalLoadingIndicator';

vi.mock('@tanstack/react-query', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@tanstack/react-query')>();
  return {
    ...actual,
    useIsFetching: vi.fn(),
  };
});

import { useIsFetching } from '@tanstack/react-query';

function renderWithQuery(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>,
  );
}

describe('GlobalLoadingIndicator', () => {
  it('fetching이 없으면 렌더링하지 않는다', () => {
    vi.mocked(useIsFetching).mockReturnValue(0);

    const { container } = renderWithQuery(<GlobalLoadingIndicator />);

    expect(container.firstChild).toBeNull();
  });

  it('fetching 중이면 프로그레스 바를 렌더링한다', () => {
    vi.mocked(useIsFetching).mockReturnValue(2);

    renderWithQuery(<GlobalLoadingIndicator />);

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });
});
