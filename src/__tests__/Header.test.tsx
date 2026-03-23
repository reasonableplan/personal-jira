import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Header } from '../components/layout/Header';

const renderHeader = (path = '/') =>
  render(
    <MemoryRouter initialEntries={[path]}>
      <Header />
    </MemoryRouter>
  );

describe('Header', () => {
  it('renders header element', () => {
    renderHeader();
    expect(screen.getByRole('banner')).toBeInTheDocument();
  });

  it('displays page title for dashboard', () => {
    renderHeader('/');
    expect(screen.getByText('대시보드')).toBeInTheDocument();
  });

  it('displays page title for board', () => {
    renderHeader('/board');
    expect(screen.getByText('보드')).toBeInTheDocument();
  });

  it('displays page title for issue detail', () => {
    renderHeader('/issues/abc-123');
    expect(screen.getByText('이슈 상세')).toBeInTheDocument();
  });

  it('has header class', () => {
    const { container } = renderHeader();
    expect(container.querySelector('.header')).toBeInTheDocument();
  });
});
