import { describe, it, expect } from 'vitest';
import { renderWithRouter, screen } from '@/test/test-utils';
import { BoardPage } from '@/pages/BoardPage';

describe('BoardPage', () => {
  it('renders with test id', () => {
    renderWithRouter(<BoardPage />);
    expect(screen.getByTestId('board-page')).toBeInTheDocument();
  });

  it('renders page heading', () => {
    renderWithRouter(<BoardPage />);
    expect(screen.getByRole('heading', { name: /보드/i })).toBeInTheDocument();
  });
});
