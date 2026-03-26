import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it } from 'vitest';

import { AppLayout } from '@/components/layout/AppLayout';
import {
  BoardPage,
  DashboardPage,
  EpicDetailPage,
  EpicsPage,
  LabelsPage,
  NotFoundPage,
} from '@/pages';

function renderWithRouter(initialPath = '/') {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="board" element={<BoardPage />} />
          <Route path="epics" element={<EpicsPage />} />
          <Route path="epics/:epicId" element={<EpicDetailPage />} />
          <Route path="labels" element={<LabelsPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

function getNav() {
  return screen.getByRole('navigation', { name: /메인 네비게이션/i });
}

describe('App routing', () => {
  it('renders dashboard page at /', () => {
    renderWithRouter('/');
    expect(
      screen.getByRole('heading', { name: /대시보드/i }),
    ).toBeInTheDocument();
  });

  it('renders board page at /board', () => {
    renderWithRouter('/board');
    expect(
      screen.getByRole('heading', { name: /^보드$/i }),
    ).toBeInTheDocument();
  });

  it('renders epics page at /epics', () => {
    renderWithRouter('/epics');
    expect(
      screen.getByRole('heading', { name: /^에픽$/i }),
    ).toBeInTheDocument();
  });

  it('renders epic detail page at /epics/1', () => {
    renderWithRouter('/epics/1');
    expect(
      screen.getByRole('heading', { name: /에픽 상세 #1/i }),
    ).toBeInTheDocument();
  });

  it('renders labels page at /labels', () => {
    renderWithRouter('/labels');
    expect(
      screen.getByRole('heading', { name: /^라벨$/i }),
    ).toBeInTheDocument();
  });

  it('renders 404 page for unknown routes', () => {
    renderWithRouter('/unknown-path');
    expect(screen.getByText('404')).toBeInTheDocument();
    expect(
      screen.getByText(/페이지를 찾을 수 없습니다/i),
    ).toBeInTheDocument();
  });
});

describe('Sidebar navigation', () => {
  it('renders the sidebar with all navigation links', () => {
    renderWithRouter('/');
    const nav = getNav();

    const dashboardLink = within(nav).getByRole('link', { name: /대시보드/i });
    expect(dashboardLink).toHaveAttribute('href', '/');

    const boardLink = within(nav).getByRole('link', { name: /^보드$/i });
    expect(boardLink).toHaveAttribute('href', '/board');

    const epicsLink = within(nav).getByRole('link', { name: /^에픽$/i });
    expect(epicsLink).toHaveAttribute('href', '/epics');

    const labelsLink = within(nav).getByRole('link', { name: /^라벨$/i });
    expect(labelsLink).toHaveAttribute('href', '/labels');
  });

  it('highlights the active navigation link', () => {
    renderWithRouter('/board');
    const nav = getNav();

    const boardLink = within(nav).getByRole('link', { name: /^보드$/i });
    expect(boardLink).toHaveAttribute('aria-current', 'page');

    const dashboardLink = within(nav).getByRole('link', { name: /대시보드/i });
    expect(dashboardLink).not.toHaveAttribute('aria-current');
  });

  it('navigates to board page when clicking board link', async () => {
    renderWithRouter('/');
    const user = userEvent.setup();
    const nav = getNav();
    await user.click(within(nav).getByRole('link', { name: /^보드$/i }));
    expect(
      await screen.findByRole('heading', { name: /^보드$/i }),
    ).toBeInTheDocument();
  });

  it('navigates to epics page when clicking epics link', async () => {
    renderWithRouter('/');
    const user = userEvent.setup();
    const nav = getNav();
    await user.click(within(nav).getByRole('link', { name: /^에픽$/i }));
    expect(
      await screen.findByRole('heading', { name: /^에픽$/i }),
    ).toBeInTheDocument();
  });

  it('navigates to labels page when clicking labels link', async () => {
    renderWithRouter('/');
    const user = userEvent.setup();
    const nav = getNav();
    await user.click(within(nav).getByRole('link', { name: /^라벨$/i }));
    expect(
      await screen.findByRole('heading', { name: /^라벨$/i }),
    ).toBeInTheDocument();
  });

  it('navigates to dashboard when clicking dashboard link', async () => {
    renderWithRouter('/board');
    const user = userEvent.setup();
    const nav = getNav();
    await user.click(within(nav).getByRole('link', { name: /대시보드/i }));
    expect(
      await screen.findByRole('heading', { name: /대시보드/i }),
    ).toBeInTheDocument();
  });
});
