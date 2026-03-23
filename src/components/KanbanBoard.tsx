import type { Issue } from '@/types/issue';
import { KANBAN_COLUMNS } from '@/types/issue';
import { IssueCard } from './IssueCard';

interface KanbanBoardProps {
  issues: Issue[];
  onIssueClick: (issue: Issue) => void;
}

export function KanbanBoard({ issues, onIssueClick }: KanbanBoardProps) {
  return (
    <div style={{ display: 'flex', gap: '1rem' }}>
      {KANBAN_COLUMNS.map(({ status, label }) => {
        const columnIssues = issues.filter((i) => i.status === status);
        return (
          <div key={status} data-testid={`column-${status}`} style={{ flex: 1 }}>
            <h3>{label}</h3>
            {columnIssues.map((issue) => (
              <IssueCard key={issue.id} issue={issue} onClick={() => onIssueClick(issue)} />
            ))}
          </div>
        );
      })}
    </div>
  );
}
