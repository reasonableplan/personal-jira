import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AppLayout } from '../components/layout/AppLayout';

const renderLayout = () =>
  render(
    <MemoryRouter>
      <AppLayout />
    </MemoryRouter>
  );

describe('AppLayout', () => {
  it('renders sidebar', () => {
    renderLayout();
    expect(screen.getByRole('complementary')).toBeInTheDocument();
  });

  it('renders header', () => {
    renderLayout();
    expect(screen.getByRole('banner')).toBeInTheDocument();
  });

  it('renders main content area', () => {
    renderLayout();
    expect(screen.getByRole('main')).toBeInTheDocument();
  });

  it('has app-layout class on root', () => {
    const { container } = renderLayout();
    expect(container.firstChild).toHaveClass('app-layout');
  });
});
