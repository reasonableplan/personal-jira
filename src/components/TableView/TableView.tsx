import type { Issue } from '@/types/issue';
import { STATUS_LABELS, PRIORITY_LABELS } from '@/types/issue';

type SortField = 'title' | 'status' | 'priority' | 'assignee';
type SortDirection = 'asc' | 'desc';

interface TableViewProps {
  issues: Issue[];
  onIssueClick: (issue: Issue) => void;
  onSort: (field: SortField) => void;
  sortField?: SortField;
  sortDirection?: SortDirection;
}

const COLUMNS: { key: SortField; label: string }[] = [
  { key: 'title', label: 'Title' },
  { key: 'status', label: 'Status' },
  { key: 'priority', label: 'Priority' },
  { key: 'assignee', label: 'Assignee' },
];

export function TableView({
  issues,
  onIssueClick,
  onSort,
  sortField,
  sortDirection,
}: TableViewProps) {
  return (
    <table data-testid="table-view">
      <thead>
        <tr>
          {COLUMNS.map((col) => (
            <th
              key={col.key}
              onClick={() => onSort(col.key)}
              style={{ cursor: 'pointer' }}
            >
              {col.label}
              {sortField === col.key && (
                <span data-testid={`sort-indicator-${col.key}`}>
                  {sortDirection === 'asc' ? '▲' : '▼'}
                </span>
              )}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {issues.length === 0 ? (
          <tr>
            <td colSpan={COLUMNS.length}>No issues found</td>
          </tr>
        ) : (
          issues.map((issue) => (
            <tr
              key={issue.id}
              data-testid="issue-row"
              data-issue-id={issue.id}
              onClick={() => onIssueClick(issue)}
              style={{ cursor: 'pointer' }}
            >
              <td>{issue.title}</td>
              <td>{STATUS_LABELS[issue.status]}</td>
              <td>{PRIORITY_LABELS[issue.priority]}</td>
              <td data-testid="assignee-cell">{issue.assignee ?? '\u2014'}</td>
            </tr>
          ))
        )}
      </tbody>
    </table>
  );
}