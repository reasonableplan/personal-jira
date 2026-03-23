import type { Issue } from '@/types/issue';

interface IssueCardProps {
  issue: Issue;
  onClick: () => void;
}

export function IssueCard({ issue, onClick }: IssueCardProps) {
  return (
    <div
      data-testid={`issue-card-${issue.id}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
      style={{ padding: '0.5rem', border: '1px solid #ddd', marginBottom: '0.5rem', cursor: 'pointer' }}
    >
      <span>{issue.title}</span>
    </div>
  );
}
