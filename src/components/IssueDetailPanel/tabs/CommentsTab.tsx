import type { Comment } from '../../../types/issue';
import { LoadingSpinner } from '../LoadingSpinner';
import styles from './Tabs.module.css';

interface CommentsTabProps {
  comments: Comment[];
  loading: boolean;
}

export function CommentsTab({ comments, loading }: CommentsTabProps) {
  if (loading) return <LoadingSpinner />;

  return (
    <div data-testid="tab-content-comments">
      {comments.length === 0 ? (
        <p className={styles.empty}>코멘트가 없습니다</p>
      ) : (
        <ul className={styles.list}>
          {comments.map((c) => (
            <li key={c.id} className={styles.listItem}>
              <div className={styles.listHeader}>
                <span className={styles.author}>{c.author}</span>
                <time className={styles.time}>{c.created_at.slice(0, 16).replace('T', ' ')}</time>
              </div>
              <p className={styles.listContent}>{c.content}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
