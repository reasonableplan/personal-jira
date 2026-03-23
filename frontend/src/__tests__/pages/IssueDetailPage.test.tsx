import { describe, it, expect } from 'vitest';
import { renderWithRouter, screen } from '@/test/test-utils';
import { IssueDetailPage } from '@/pages/IssueDetailPage';

describe('IssueDetailPage', () => {
  it('renders with test id', () => {
    renderWithRouter(<IssueDetailPage />, {
      routerProps: { initialEntries: ['/issues/test-id-123'] },
    });
    expect(screen.getByTestId('issue-detail-page')).toBeInTheDocument();
  });

  it('renders page heading', () => {
    renderWithRouter(<IssueDetailPage />, {
      routerProps: { initialEntries: ['/issues/test-id-123'] },
    });
    expect(screen.getByRole('heading', { name: /이슈 상세/i })).toBeInTheDocument();
  });
});
