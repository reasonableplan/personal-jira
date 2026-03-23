import { describe, it, expect } from 'vitest';
import { screen } from '@/test/test-utils';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '@/App';

function renderApp(initialRoute = '/') {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <App />
    </MemoryRouter>,
  );
}

describe('App routing', () => {
  it('renders dashboard at root path', () => {
    renderApp('/');
    expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
  });

  it('renders board page at /board', () => {
    renderApp('/board');
    expect(screen.getByTestId('board-page')).toBeInTheDocument();
  });

  it('renders issue detail page at /issues/:id', () => {
    renderApp('/issues/abc-123');
    expect(screen.getByTestId('issue-detail-page')).toBeInTheDocument();
  });

  it('renders not-found page for unknown routes', () => {
    renderApp('/unknown-route');
    expect(screen.getByTestId('not-found-page')).toBeInTheDocument();
  });

  it('renders layout with sidebar and header on all pages', () => {
    renderApp('/');
    expect(screen.getByTestId('app-sidebar')).toBeInTheDocument();
    expect(screen.getByTestId('app-header')).toBeInTheDocument();
  });
});
