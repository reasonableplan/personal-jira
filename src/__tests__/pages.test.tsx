import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { Dashboard } from '../pages/Dashboard';
import { Board } from '../pages/Board';
import { IssueDetail } from '../pages/IssueDetail';
import { NotFound } from '../pages/NotFound';

describe('Dashboard', () => {
  it('renders dashboard heading', () => {
    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );
    expect(screen.getByRole('heading', { name: '대시보드' })).toBeInTheDocument();
  });

  it('renders summary section', () => {
    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    );
    expect(screen.getByText('이슈 요약')).toBeInTheDocument();
  });
});

describe('Board', () => {
  it('renders board heading', () => {
    render(
      <MemoryRouter>
        <Board />
      </MemoryRouter>
    );
    expect(screen.getByRole('heading', { name: '보드' })).toBeInTheDocument();
  });

  it('renders status columns', () => {
    render(
      <MemoryRouter>
        <Board />
      </MemoryRouter>
    );
    expect(screen.getByText('Backlog')).toBeInTheDocument();
    expect(screen.getByText('Ready')).toBeInTheDocument();
    expect(screen.getByText('In Progress')).toBeInTheDocument();
    expect(screen.getByText('Done')).toBeInTheDocument();
  });
});

describe('IssueDetail', () => {
  const renderWithRoute = (id: string) =>
    render(
      <MemoryRouter initialEntries={[`/issues/${id}`]}>
        <Routes>
          <Route path="/issues/:id" element={<IssueDetail />} />
        </Routes>
      </MemoryRouter>
    );

  it('renders issue detail heading', () => {
    renderWithRoute('abc-123');
    expect(screen.getByRole('heading', { name: '이슈 상세' })).toBeInTheDocument();
  });

  it('displays issue id from route params', () => {
    renderWithRoute('abc-123');
    expect(screen.getByText('abc-123')).toBeInTheDocument();
  });
});

describe('NotFound', () => {
  it('renders 404 message', () => {
    render(
      <MemoryRouter>
        <NotFound />
      </MemoryRouter>
    );
    expect(screen.getByText('404')).toBeInTheDocument();
    expect(screen.getByText('페이지를 찾을 수 없습니다')).toBeInTheDocument();
  });

  it('renders link to dashboard', () => {
    render(
      <MemoryRouter>
        <NotFound />
      </MemoryRouter>
    );
    const link = screen.getByRole('link', { name: '대시보드로 돌아가기' });
    expect(link).toHaveAttribute('href', '/');
  });
});
