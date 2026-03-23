import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { IssueCard } from '@/components/IssueCard';
import type { Issue } from '@/types/issue';

const MOCK_ISSUE: Issue = {
  id: 'card-1',
  title: 'Fix login bug',
  description: 'Users cannot login',
  status: 'InProgress',
  priority: 'High',
  parent_id: null,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('IssueCard', () => {
  it('renders issue title', () => {
    render(<IssueCard issue={MOCK_ISSUE} />);
    expect(screen.getByText('Fix login bug')).toBeInTheDocument();
  });

  it('renders priority badge', () => {
    render(<IssueCard issue={MOCK_ISSUE} />);
    expect(screen.getByText('High')).toBeInTheDocument();
  });

  it('renders description when present', () => {
    render(<IssueCard issue={MOCK_ISSUE} />);
    expect(screen.getByText('Users cannot login')).toBeInTheDocument();
  });

  it('does not render description when null', () => {
    const issue = { ...MOCK_ISSUE, description: null };
    render(<IssueCard issue={issue} />);
    expect(screen.queryByTestId('card-description')).not.toBeInTheDocument();
  });

  it('has draggable data attribute', () => {
    render(<IssueCard issue={MOCK_ISSUE} />);
    const card = screen.getByTestId('issue-card-card-1');
    expect(card).toBeInTheDocument();
  });
});
