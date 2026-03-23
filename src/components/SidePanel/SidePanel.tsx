import type { Issue } from '@/types/issue';
import { STATUS_LABELS, PRIORITY_LABELS } from '@/types/issue';

interface SidePanelProps {
  issue: Issue | null;
  open: boolean;
  onClose: () => void;
  onEdit: (issue: Issue) => void;
  onDelete: (issueId: string) => void;
}

export function SidePanel({ issue, open, onClose, onEdit, onDelete }: SidePanelProps) {
  if (!open) return null;

  if (!issue) {
    return (
      <aside role="complementary">
        <p>No issue selected</p>
        <button data-testid="close-button" onClick={onClose}>
          Close
        </button>
      </aside>
    );
  }

  return (
    <aside role="complementary">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>{issue.title}</h2>
        <button data-testid="close-button" onClick={onClose} aria-label="Close">
          ×
        </button>
      </div>
      <p>{issue.description}</p>
      <dl>
        <dt>Status</dt>
        <dd>{STATUS_LABELS[issue.status]}</dd>
        <dt>Priority</dt>
        <dd>{PRIORITY_LABELS[issue.priority]}</dd>
        <dt>Assignee</dt>
        <dd>{issue.assignee ?? 'Unassigned'}</dd>
      </dl>
      <div>
        <time data-testid="created-at" dateTime={issue.created_at}>
          Created: {new Date(issue.created_at).toLocaleDateString()}
        </time>
        <time data-testid="updated-at" dateTime={issue.updated_at}>
          Updated: {new Date(issue.updated_at).toLocaleDateString()}
        </time>
      </div>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <button data-testid="edit-button" onClick={() => onEdit(issue)}>
          Edit
        </button>
        <button data-testid="delete-button" onClick={() => onDelete(issue.id)}>
          Delete
        </button>
      </div>
    </aside>
  );
}