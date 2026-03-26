import { render, screen } from '@testing-library/react';
import { createMemoryRouter, RouterProvider } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { AppLayout } from '@/components/layout/AppLayout';

function renderLayout(initialEntries: string[] = ['/']) {
  const router = createMemoryRouter(
    [
      {
        element: <AppLayout />,
        children: [
          { index: true, element: <div>Dashboard Content</div> },
          { path: 'board', element: <div>Board Content</div> },
          { path: 'epics', element: <div>Epics Content</div> },
          { path: 'labels', element: <div>Labels Content</div> },
        ],
      },
    ],
    { initialEntries },
  );
  return render(<RouterProvider router={router} />);
}

describe('AppLayout', () => {
  it('renders navigation links with correct hrefs', () => {
    renderLayout();
    const nav = screen.getByRole('navigation', { name: /메인 네비게이션/i });
    expect(nav).toBeInTheDocument();

    const dashboardLink = screen.getByRole('link', { name: /대시보드/i });
    expect(dashboardLink).toHaveAttribute('href', '/');

    const epicsLink = screen.getByRole('link', { name: /^에픽$/i });
    expect(epicsLink).toHaveAttribute('href', '/epics');

    const labelsLink = screen.getByRole('link', { name: /^라벨$/i });
    expect(labelsLink).toHaveAttribute('href', '/labels');
  });

  it('renders child content via Outlet', () => {
    renderLayout(['/']);
    expect(screen.getByText('Dashboard Content')).toBeInTheDocument();
  });

  it('renders correct content for board route', () => {
    renderLayout(['/board']);
    expect(screen.getByText('Board Content')).toBeInTheDocument();
  });

  it('highlights active nav link', () => {
    renderLayout(['/board']);
    const links = screen.getAllByRole('link');
    const boardLink = links.find((link) => link.textContent?.trim() === '보드');
    expect(boardLink).toHaveAttribute('aria-current', 'page');

    const dashboardLink = screen.getByRole('link', { name: /대시보드/i });
    expect(dashboardLink).not.toHaveAttribute('aria-current');
  });

  it('renders mobile menu button', () => {
    renderLayout();
    expect(
      screen.getByRole('button', { name: /메뉴 열기/i }),
    ).toBeInTheDocument();
  });
});
