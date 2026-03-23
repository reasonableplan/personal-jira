import { useState, useEffect, useCallback } from 'react';
import type { Comment } from '@/types/issue';
import { api } from '@/api/client';

export function useComments(issueId: string | null) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!issueId) {
      setComments([]);
      return;
    }
    setLoading(true);
    api
      .getComments(issueId)
      .then(setComments)
      .catch(() => setComments([]))
      .finally(() => setLoading(false));
  }, [issueId]);

  const addComment = useCallback(
    async (content: string) => {
      if (!issueId) return;
      const comment = await api.createComment(issueId, { content });
      setComments((prev) => [...prev, comment]);
    },
    [issueId],
  );

  return { comments, loading, addComment };
}
