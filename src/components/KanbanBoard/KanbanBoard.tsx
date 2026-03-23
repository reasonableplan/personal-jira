import type { Issue, IssueStatus } from '@/types/issue';
import { KANBAN_COLUMNS, STATUS_LABELS, PRIORITY_LABELS } from '@/types/issue';

interface KanbanBoardProps {
  issues: Issue[];
  onIssueClick: (issue: Issue) => void;
  onStatusChange: (issueId: string, status: IssueStatus) => void;
}

export function KanbanBoard({ issues, onIssueClick }: KanbanBoardProps) {
  const issuesByStatus = KANBAN_COLUMNS.reduce(
    (acc, status) => {
      acc[status] = issues.filter((issue) => issue.status === status);
      return acc;
    },
    {} as Record<IssueStatus, Issue[]>
  );

  return (
    <div data-testid="kanban-board" style={{ display: 'flex', gap: '1rem' }}>
      {KANBAN_COLUMNS.map((status) => (
        <div key={status} data-testid={`column-${status}`} style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <h2>{STATUS_LABELS[status]}</h2>
            <span data-testid="issue-count">{issuesByStatus[status].length}</span>
          </div>
          {issuesByStatus[status].length === 0 ? (
            <p>No issues</p>
          ) : (
            issuesByStatus[status].map((issue) => (
              <div
                key={issue.id}
                data-testid="issue-card"
                data-issue-id={issue.id}
                onClick={() => onIssueClick(issue)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') onIssueClick(issue);
                }}
              >
                <span>{issue.title}</span>
                <span data-testid="priority-badge">
                  {PRIORITY_LABELS[issue.priority]}
                </span>
                {issue.assignee && <span>{issue.assignee}</span>}
              </div>
            ))
          )}
        </div>
      ))}
    </div>
  );
}