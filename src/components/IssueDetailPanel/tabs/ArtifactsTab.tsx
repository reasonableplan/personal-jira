import type { Artifact } from '../../../types/issue';
import { LoadingSpinner } from '../LoadingSpinner';
import styles from './Tabs.module.css';

interface ArtifactsTabProps {
  artifacts: Artifact[];
  loading: boolean;
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function ArtifactsTab({ artifacts, loading }: ArtifactsTabProps) {
  if (loading) return <LoadingSpinner />;

  return (
    <div data-testid="tab-content-artifacts">
      {artifacts.length === 0 ? (
        <p className={styles.empty}>아티팩트가 없습니다</p>
      ) : (
        <ul className={styles.list}>
          {artifacts.map((a) => (
            <li key={a.id} className={styles.listItem}>
              <div className={styles.artifactRow}>
                <a href={a.url} className={styles.filename} target="_blank" rel="noopener noreferrer">
                  {a.filename}
                </a>
                <span className={styles.fileSize}>{formatBytes(a.size_bytes)}</span>
              </div>
              <time className={styles.time}>{a.uploaded_at.slice(0, 16).replace('T', ' ')}</time>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
