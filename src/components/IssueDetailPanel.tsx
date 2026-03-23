import { IssueStatus, STATUS_LABELS } from '@/types/issue';
import type { Issue } from '@/types/issue';
import { CommentSection } from './CommentSection';

interface IssueDetailPanelProps {
  issue: Issue;
  onClose: () => void;
  onStatusChange: (id: string, status: IssueStatus) => Promise<void>;
}

const SELECTABLE_STATUSES = [
  IssueStatus.BACKLOG,
  IssueStatus.READY,
  IssueStatus.IN_PROGRESS,
  IssueStatus.IN_REVIEW,
  IssueStatus.DONE,
  IssueStatus.CANCELLED,
  IssueStatus.BLOCKED,
];

export function IssueDetailPanel({ issue, onClose, onStatusChange }: IssueDetailPanelProps) {
  return (
    <div data-testid="issue-detail-panel" style={{ padding: '1rem', border: '1px solid #ccc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <h2>{issue.title}</h2>
        <button onClick={onClose} aria-label="닫기">
          ×
        </button>
      </div>
      <p>{issue.description}</p>
      <div>
        <label htmlFor="status-select">상태</label>
        <select
          id="status-select"
          value={issue.status}
          onChange={(e) => onStatusChange(issue.id, e.target.value as IssueStatus)}
        >
          {SELECTABLE_STATUSES.map((s) => (
            <option key={s} value={s}>
              {STATUS_LABELS[s]}
            </option>
          ))}
        </select>
      </div>
      <CommentSection issueId={issue.id} />
    </div>
  );
}
