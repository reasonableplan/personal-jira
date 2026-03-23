import { useEffect } from 'react';
import type { Issue } from '../../types/issue';
import { TAB_KEYS, TAB_LABELS } from './constants';
import type { TabKey } from './constants';
import { useIssueDetail } from './useIssueDetail';
import { DetailTab } from './tabs/DetailTab';
import { CommentsTab } from './tabs/CommentsTab';
import { LogsTab } from './tabs/LogsTab';
import { ArtifactsTab } from './tabs/ArtifactsTab';
import styles from './IssueDetailPanel.module.css';

interface IssueDetailPanelProps {
  issue: Issue | null;
  open: boolean;
  onClose: () => void;
}

export function IssueDetailPanel({ issue, open, onClose }: IssueDetailPanelProps) {
  const {
    activeTab,
    setActiveTab,
    comments,
    logs,
    artifacts,
    commentsLoading,
    logsLoading,
    artifactsLoading,
    error,
  } = useIssueDetail(issue?.id ?? null);

  useEffect(() => {
    if (!open) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [open, onClose]);

  if (!open || !issue) return null;

  const renderTabContent = () => {
    switch (activeTab) {
      case 'detail':
        return <DetailTab issue={issue} />;
      case 'comments':
        return <CommentsTab comments={comments} loading={commentsLoading} />;
      case 'logs':
        return <LogsTab logs={logs} loading={logsLoading} />;
      case 'artifacts':
        return <ArtifactsTab artifacts={artifacts} loading={artifactsLoading} />;
    }
  };

  return (
    <>
      <div
        className={styles.overlay}
        data-testid="panel-overlay"
        onClick={onClose}
      />
      <aside
        className={`${styles.panel} ${styles.slideIn}`}
        data-testid="issue-detail-panel"
      >
        <div className={styles.header}>
          <h2 className={styles.title}>{issue.title}</h2>
          <button
            className={styles.closeBtn}
            onClick={onClose}
            aria-label="Close panel"
          >
            ×
          </button>
        </div>

        {error && <div className={styles.errorBanner}>{error}</div>}

        <div className={styles.tabBar} role="tablist">
          {TAB_KEYS.map((key) => (
            <button
              key={key}
              role="tab"
              aria-selected={activeTab === key}
              className={`${styles.tab} ${activeTab === key ? styles.tabActive : ''}`}
              onClick={() => setActiveTab(key)}
            >
              {TAB_LABELS[key]}
            </button>
          ))}
        </div>

        <div className={styles.content}>
          {renderTabContent()}
        </div>
      </aside>
    </>
  );
}
