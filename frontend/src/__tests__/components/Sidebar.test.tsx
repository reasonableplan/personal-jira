import { describe, it, expect } from 'vitest';
import { renderWithRouter, screen } from '@/test/test-utils';
import { Sidebar } from '@/components/Sidebar';

describe('Sidebar', () => {
  it('renders navigation links', () => {
    renderWithRouter(<Sidebar />);
    expect(screen.getByRole('link', { name: /대시보드/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /보드/i })).toBeInTheDocument();
  });

  it('links to correct paths', () => {
    renderWithRouter(<Sidebar />);
    expect(screen.getByRole('link', { name: /대시보드/i })).toHaveAttribute('href', '/');
    expect(screen.getByRole('link', { name: /보드/i })).toHaveAttribute('href', '/board');
  });

  it('renders app title', () => {
    renderWithRouter(<Sidebar />);
    expect(screen.getByText('Personal Jira')).toBeInTheDocument();
  });

  it('highlights active link', () => {
    renderWithRouter(<Sidebar />, {
      routerProps: { initialEntries: ['/board'] },
    });
    const boardLink = screen.getByRole('link', { name: /보드/i });
    expect(boardLink).toHaveClass('active');
  });
});
