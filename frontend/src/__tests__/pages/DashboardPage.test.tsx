import { describe, it, expect } from 'vitest';
import { renderWithRouter, screen } from '@/test/test-utils';
import { DashboardPage } from '@/pages/DashboardPage';

describe('DashboardPage', () => {
  it('renders with test id', () => {
    renderWithRouter(<DashboardPage />);
    expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
  });

  it('renders page heading', () => {
    renderWithRouter(<DashboardPage />);
    expect(screen.getByRole('heading', { name: /대시보드/i })).toBeInTheDocument();
  });
});
