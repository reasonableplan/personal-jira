import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach, type Mock } from 'vitest';
import { IssueTable } from '../../src/components/IssueTable/IssueTable';
import { fetchIssues } from '../../src/api/issues';
import { Issue, IssueStatus, IssuePriority, IssueType, PaginatedResponse } from '../../src/types/issue';

vi.mock('../../src/api/issues');

const mockFetchIssues = fetchIssues as Mock;

function createIssue(overrides: Partial<Issue> = {}): Issue {
  return {
    id: crypto.randomUUID(),
    title: 'Test Issue',
    description: null,
    issue_type: IssueType.TASK,
    status: IssueStatus.TODO,
    priority: IssuePriority.MEDIUM,
    assignee: null,
    labels: [],
    required_skills: [],
    parent_id: null,
    context_bundle: null,
    created_at: '2026-03-20T10:00:00Z',
    updated_at: '2026-03-20T10:00:00Z',
    ...overrides,
  };
}

function createPaginatedResponse(
  items: Issue[],
  overrides: Partial<PaginatedResponse<Issue>> = {}
): PaginatedResponse<Issue> {
  return {
    items,
    total: items.length,
    page: 1,
    page_size: 20,
    total_pages: 1,
    ...overrides,
  };
}

describe('IssueTable', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state initially', () => {
    mockFetchIssues.mockReturnValue(new Promise(() => {}));
    render(<IssueTable />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('renders issue rows after loading', async () => {
    const issues = [
      createIssue({ title: 'First Issue' }),
      createIssue({ title: 'Second Issue' }),
    ];
    mockFetchIssues.mockResolvedValue(createPaginatedResponse(issues));

    render(<IssueTable />);

    await waitFor(() => {
      expect(screen.getByText('First Issue')).toBeInTheDocument();
    });
    expect(screen.getByText('Second Issue')).toBeInTheDocument();
  });

  it('renders error state on fetch failure', async () => {
    mockFetchIssues.mockRejectedValue(new Error('Network error'));

    render(<IssueTable />);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
    expect(screen.getByText(/Network error/)).toBeInTheDocument();
  });

  it('renders empty state when no issues', async () => {
    mockFetchIssues.mockResolvedValue(createPaginatedResponse([]));

    render(<IssueTable />);

    await waitFor(() => {
      expect(screen.getByText(/no issues found/i)).toBeInTheDocument();
    });
  });

  it('displays all table columns', async () => {
    mockFetchIssues.mockResolvedValue(createPaginatedResponse([createIssue()]));

    render(<IssueTable />);

    await waitFor(() => {
      expect(screen.getByText('Title')).toBeInTheDocument();
    });
    expect(screen.getByText('Type')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('Priority')).toBeInTheDocument();
    expect(screen.getByText('Assignee')).toBeInTheDocument();
    expect(screen.getByText('Created')).toBeInTheDocument();
  });

  it('renders status and priority badges', async () => {
    const issue = createIssue({
      status: IssueStatus.IN_PROGRESS,
      priority: IssuePriority.HIGH,
    });
    mockFetchIssues.mockResolvedValue(createPaginatedResponse([issue]));

    render(<IssueTable />);

    await waitFor(() => {
      expect(screen.getByText('In Progress')).toBeInTheDocument();
    });
    expect(screen.getByText('High')).toBeInTheDocument();
  });

  it('calls fetchIssues with sort params on column header click', async () => {
    mockFetchIssues.mockResolvedValue(createPaginatedResponse([createIssue()]));

    render(<IssueTable />);

    await waitFor(() => {
      expect(screen.getByText('Title')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Title'));

    await waitFor(() => {
      expect(mockFetchIssues).toHaveBeenCalledWith(
        1, 20, {}, 'title', 'asc'
      );
    });
  });

  it('toggles sort order on repeated column header click', async () => {
    mockFetchIssues.mockResolvedValue(createPaginatedResponse([createIssue()]));

    render(<IssueTable />);

    await waitFor(() => {
      expect(screen.getByText('Title')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Title'));
    await waitFor(() => {
      expect(mockFetchIssues).toHaveBeenCalledWith(1, 20, {}, 'title', 'asc');
    });

    fireEvent.click(screen.getByText('Title'));
    await waitFor(() => {
      expect(mockFetchIssues).toHaveBeenCalledWith(1, 20, {}, 'title', 'desc');
    });
  });

  it('filters by status', async () => {
    const user = userEvent.setup();
    mockFetchIssues.mockResolvedValue(createPaginatedResponse([createIssue()]));

    render(<IssueTable />);

    await waitFor(() => {
      expect(screen.getByLabelText('Filter by status')).toBeInTheDocument();
    });

    await user.selectOptions(screen.getByLabelText('Filter by status'), IssueStatus.IN_PROGRESS);

    await waitFor(() => {
      expect(mockFetchIssues).toHaveBeenCalledWith(
        1, 20, expect.objectContaining({ status: IssueStatus.IN_PROGRESS }), undefined, undefined
      );
    });
  });

  it('filters by priority', async () => {
    const user = userEvent.setup();
    mockFetchIssues.mockResolvedValue(createPaginatedResponse([createIssue()]));

    render(<IssueTable />);

    await waitFor(() => {
      expect(screen.getByLabelText('Filter by priority')).toBeInTheDocument();
    });

    await user.selectOptions(screen.getByLabelText('Filter by priority'), IssuePriority.HIGH);

    await waitFor(() => {
      expect(mockFetchIssues).toHaveBeenCalledWith(
        1, 20, expect.objectContaining({ priority: IssuePriority.HIGH }), undefined, undefined
      );
    });
  });

  it('searches issues by text input', async () => {
    const user = userEvent.setup();
    mockFetchIssues.mockResolvedValue(createPaginatedResponse([createIssue()]));

    render(<IssueTable />);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Search issues...')).toBeInTheDocument();
    });

    await user.type(screen.getByPlaceholderText('Search issues...'), 'bug fix');

    await waitFor(() => {
      expect(mockFetchIssues).toHaveBeenCalledWith(
        1, 20, expect.objectContaining({ search: 'bug fix' }), undefined, undefined
      );
    }, { timeout: 1000 });
  });

  it('paginates to next page', async () => {
    const issues = Array.from({ length: 20 }, (_, i) =>
      createIssue({ title: `Issue ${i + 1}` })
    );
    mockFetchIssues.mockResolvedValue(
      createPaginatedResponse(issues, { total: 40, total_pages: 2 })
    );

    render(<IssueTable />);

    await waitFor(() => {
      expect(screen.getByText('Issue 1')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByLabelText('Next page'));

    await waitFor(() => {
      expect(mockFetchIssues).toHaveBeenCalledWith(
        2, 20, {}, undefined, undefined
      );
    });
  });

  it('disables previous button on first page', async () => {
    mockFetchIssues.mockResolvedValue(
      createPaginatedResponse([createIssue()], { page: 1, total_pages: 3 })
    );

    render(<IssueTable />);

    await waitFor(() => {
      expect(screen.getByLabelText('Previous page')).toBeDisabled();
    });
  });

  it('disables next button on last page', async () => {
    mockFetchIssues.mockResolvedValue(
      createPaginatedResponse([createIssue()], { page: 3, total_pages: 3 })
    );

    render(<IssueTable />);

    await waitFor(() => {
      expect(screen.getByLabelText('Next page')).toBeDisabled();
    });
  });

  it('changes page size', async () => {
    const user = userEvent.setup();
    mockFetchIssues.mockResolvedValue(
      createPaginatedResponse([createIssue()], { total: 50, total_pages: 3 })
    );

    render(<IssueTable />);

    await waitFor(() => {
      expect(screen.getByLabelText('Page size')).toBeInTheDocument();
    });

    await user.selectOptions(screen.getByLabelText('Page size'), '50');

    await waitFor(() => {
      expect(mockFetchIssues).toHaveBeenCalledWith(
        1, 50, {}, undefined, undefined
      );
    });
  });

  it('shows page info text', async () => {
    mockFetchIssues.mockResolvedValue(
      createPaginatedResponse([createIssue()], { page: 2, total: 45, total_pages: 3 })
    );

    render(<IssueTable />);

    await waitFor(() => {
      expect(screen.getByText(/page 2 of 3/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/45 total/i)).toBeInTheDocument();
  });

  it('resets to page 1 when filters change', async () => {
    const user = userEvent.setup();
    mockFetchIssues.mockResolvedValue(
      createPaginatedResponse([createIssue()], { page: 2, total: 40, total_pages: 2 })
    );

    render(<IssueTable />);

    await waitFor(() => {
      expect(screen.getByLabelText('Filter by status')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByLabelText('Next page'));

    await user.selectOptions(screen.getByLabelText('Filter by status'), IssueStatus.DONE);

    await waitFor(() => {
      const lastCall = mockFetchIssues.mock.calls[mockFetchIssues.mock.calls.length - 1];
      expect(lastCall[0]).toBe(1);
    });
  });
});
