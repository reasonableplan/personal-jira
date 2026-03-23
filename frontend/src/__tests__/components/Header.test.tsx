import { describe, it, expect } from 'vitest';
import { renderWithRouter, screen } from '@/test/test-utils';
import { Header } from '@/components/Header';

describe('Header', () => {
  it('renders header element', () => {
    renderWithRouter(<Header />);
    expect(screen.getByTestId('app-header')).toBeInTheDocument();
  });

  it('renders breadcrumb or page title area', () => {
    renderWithRouter(<Header />);
    expect(screen.getByTestId('header-title')).toBeInTheDocument();
  });
});
