import { describe, it, expect } from 'vitest';
import { renderWithRouter, screen } from '@/test/test-utils';
import { AppLayout } from '@/layouts/AppLayout';

describe('AppLayout', () => {
  it('renders sidebar', () => {
    renderWithRouter(<AppLayout />);
    expect(screen.getByTestId('app-sidebar')).toBeInTheDocument();
  });

  it('renders header', () => {
    renderWithRouter(<AppLayout />);
    expect(screen.getByTestId('app-header')).toBeInTheDocument();
  });

  it('renders main content area', () => {
    renderWithRouter(<AppLayout />);
    expect(screen.getByTestId('app-main')).toBeInTheDocument();
  });

  it('has correct layout structure', () => {
    const { container } = renderWithRouter(<AppLayout />);
    const layout = container.firstElementChild;
    expect(layout).toHaveClass('app-layout');
  });
});
