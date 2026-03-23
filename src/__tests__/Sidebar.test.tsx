import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Sidebar } from '../components/layout/Sidebar';
import { ROUTES } from '../constants/routes';

const renderSidebar = (initialPath = '/') =>
  render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Sidebar />
    </MemoryRouter>
  );

describe('Sidebar', () => {
  it('renders navigation', () => {
    renderSidebar();
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });

  it('renders app title', () => {
    renderSidebar();
    expect(screen.getByText('Personal Jira')).toBeInTheDocument();
  });

  it('renders dashboard link', () => {
    renderSidebar();
    const link = screen.getByRole('link', { name: '대시보드' });
    expect(link).toHaveAttribute('href', ROUTES.DASHBOARD);
  });

  it('renders board link', () => {
    renderSidebar();
    const link = screen.getByRole('link', { name: '보드' });
    expect(link).toHaveAttribute('href', ROUTES.BOARD);
  });

  it('highlights active link for dashboard', () => {
    renderSidebar('/');
    const link = screen.getByRole('link', { name: '대시보드' });
    expect(link).toHaveClass('active');
  });

  it('highlights active link for board', () => {
    renderSidebar('/board');
    const link = screen.getByRole('link', { name: '보드' });
    expect(link).toHaveClass('active');
  });
});
