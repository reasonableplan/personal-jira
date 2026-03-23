import { describe, it, expect } from 'vitest';
import { renderWithRouter, screen } from '@/test/test-utils';
import { NotFoundPage } from '@/pages/NotFoundPage';

describe('NotFoundPage', () => {
  it('renders with test id', () => {
    renderWithRouter(<NotFoundPage />);
    expect(screen.getByTestId('not-found-page')).toBeInTheDocument();
  });

  it('renders 404 message', () => {
    renderWithRouter(<NotFoundPage />);
    expect(screen.getByText(/404/)).toBeInTheDocument();
  });

  it('renders link back to dashboard', () => {
    renderWithRouter(<NotFoundPage />);
    expect(screen.getByRole('link', { name: /대시보드/i })).toHaveAttribute('href', '/');
  });
});
