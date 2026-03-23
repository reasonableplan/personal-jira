import { useState } from 'react';
import { useComments } from '@/hooks/useComments';

interface CommentSectionProps {
  issueId: string;
}

export function CommentSection({ issueId }: CommentSectionProps) {
  const { comments, addComment } = useComments(issueId);
  const [content, setContent] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (!content.trim()) return;
    setSubmitting(true);
    try {
      await addComment(content.trim());
      setContent('');
    } catch (err) {
      console.error('Failed to add comment:', err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <h3>코멘트</h3>
      <div>
        {comments.map((c) => (
          <div key={c.id} data-testid="comment-item">
            <strong>{c.author}</strong>
            <p>{c.content}</p>
          </div>
        ))}
      </div>
      <textarea
        placeholder="코멘트를 입력하세요"
        value={content}
        onChange={(e) => setContent(e.target.value)}
      />
      <button onClick={handleSubmit} disabled={submitting}>
        등록
      </button>
    </div>
  );
}
