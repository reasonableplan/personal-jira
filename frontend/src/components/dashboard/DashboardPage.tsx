import { useDashboard } from '@/hooks/useDashboard';
import { CompletionRateChart } from './CompletionRateChart';
import { AgentBarChart } from './AgentBarChart';
import { AgentStatsCard } from './AgentStatsCard';
import styles from './Dashboard.module.css';

export function DashboardPage() {
  const { data, loading, error, refetch } = useDashboard();

  if (loading) {
    return <div className={styles.loading}>로딩 중...</div>;
  }

  if (error) {
    return (
      <div className={styles.error}>
        <p>{error}</p>
        <button type="button" className={styles.retryButton} onClick={refetch}>
          재시도
        </button>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className={styles.page}>
      <h2 className={styles.pageTitle}>대시보드</h2>

      <div className={styles.summaryRow}>
        <div className={styles.summaryCard}>
          <span className={styles.summaryValue}>{data.totalIssues}</span>
          <span className={styles.summaryLabel}>전체 이슈</span>
        </div>
        <div className={styles.summaryCard}>
          <span className={styles.summaryValue}>{data.completedIssues}</span>
          <span className={styles.summaryLabel}>완료 이슈</span>
        </div>
        <div className={styles.summaryCard}>
          <span className={styles.summaryValue}>{data.completionRate}%</span>
          <span className={styles.summaryLabel}>완료율</span>
        </div>
      </div>

      <div className={styles.chartsRow}>
        <CompletionRateChart
          statusCounts={data.statusCounts}
          completionRate={data.completionRate}
        />
        <AgentBarChart agents={data.agentStats} />
      </div>

      <section className={styles.agentSection}>
        <h3 className={styles.sectionTitle}>에이전트 통계</h3>
        <div className={styles.agentGrid}>
          {data.agentStats.map((agent) => (
            <AgentStatsCard key={agent.agentId} agent={agent} />
          ))}
        </div>
      </section>
    </div>
  );
}
