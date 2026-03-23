import { useState } from 'react';

interface CreateIssueDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (title: string, description: string) => Promise<void>;
}

export function CreateIssueDialog({ open, onClose, onSubmit }: CreateIssueDialogProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (!open) return null;

  const handleSubmit = async () => {
    if (!title.trim()) {
      setError('제목은 필수입니다');
      return;
    }
    setSubmitting(true);
    try {
      await onSubmit(title.trim(), description.trim());
      setTitle('');
      setDescription('');
      setError('');
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : '생성 실패');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div role="dialog" aria-label="이슈 생성">
      <div>
        <label htmlFor="issue-title">제목</label>
        <input
          id="issue-title"
          value={title}
          onChange={(e) => {
            setTitle(e.target.value);
            setError('');
          }}
        />
      </div>
      <div>
        <label htmlFor="issue-description">설명</label>
        <textarea
          id="issue-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>
      {error && <p>{error}</p>}
      <button onClick={handleSubmit} disabled={submitting}>
        생성
      </button>
      <button onClick={onClose}>취소</button>
    </div>
  );
}
