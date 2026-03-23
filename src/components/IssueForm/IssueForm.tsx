import { useState, type FormEvent } from 'react';
import type { Issue, IssueStatus, IssuePriority } from '@/types/issue';
import {
  ISSUE_STATUS,
  ISSUE_PRIORITY,
  STATUS_LABELS,
  PRIORITY_LABELS,
  KANBAN_COLUMNS,
} from '@/types/issue';

interface IssueFormData {
  title: string;
  description: string;
  status: IssueStatus;
  priority: IssuePriority;
  assignee: string;
}

interface IssueFormProps {
  issue?: Issue;
  onSubmit: (data: IssueFormData) => void;
  onCancel: () => void;
}

const PRIORITY_OPTIONS: IssuePriority[] = [
  ISSUE_PRIORITY.LOW,
  ISSUE_PRIORITY.MEDIUM,
  ISSUE_PRIORITY.HIGH,
  ISSUE_PRIORITY.URGENT,
];

export function IssueForm({ issue, onSubmit, onCancel }: IssueFormProps) {
  const isEdit = Boolean(issue);

  const [title, setTitle] = useState(issue?.title ?? '');
  const [description, setDescription] = useState(issue?.description ?? '');
  const [status, setStatus] = useState<IssueStatus>(issue?.status ?? ISSUE_STATUS.BACKLOG);
  const [priority, setPriority] = useState<IssuePriority>(issue?.priority ?? ISSUE_PRIORITY.MEDIUM);
  const [assignee, setAssignee] = useState(issue?.assignee ?? '');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError('Title is required');
      return;
    }
    onSubmit({ title: title.trim(), description, status, priority, assignee });
  };

  const handleTitleChange = (value: string) => {
    setTitle(value);
    if (error) setError(null);
  };

  return (
    <form onSubmit={handleSubmit} data-testid="issue-form">
      <div>
        <label htmlFor="issue-title">Title</label>
        <input
          id="issue-title"
          value={title}
          onChange={(e) => handleTitleChange(e.target.value)}
        />
        {error && <span role="alert">{error}</span>}
      </div>
      <div>
        <label htmlFor="issue-description">Description</label>
        <textarea
          id="issue-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>
      <div>
        <label htmlFor="issue-status">Status</label>
        <select
          id="issue-status"
          value={status}
          onChange={(e) => setStatus(e.target.value as IssueStatus)}
        >
          {KANBAN_COLUMNS.map((s) => (
            <option key={s} value={s}>
              {STATUS_LABELS[s]}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="issue-priority">Priority</label>
        <select
          id="issue-priority"
          value={priority}
          onChange={(e) => setPriority(e.target.value as IssuePriority)}
        >
          {PRIORITY_OPTIONS.map((p) => (
            <option key={p} value={p}>
              {PRIORITY_LABELS[p]}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="issue-assignee">Assignee</label>
        <input
          id="issue-assignee"
          value={assignee}
          onChange={(e) => setAssignee(e.target.value)}
        />
      </div>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <button type="submit" data-testid="submit-button">
          {isEdit ? 'Save' : 'Create'}
        </button>
        <button type="button" data-testid="cancel-button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  );
}