import type { AgentStats } from '@/types/dashboard';
import styles from './Dashboard.module.css';

interface AgentStatsCardProps {
  agent: AgentStats;
}

export function AgentStatsCard({ agent }: AgentStatsCardProps) {
  return (
    <div className={styles.agentCard}>
      <h4 className={styles.agentName}>{agent.name}</h4>
      <div className={styles.agentMetrics}>
        <div className={styles.metric}>
          <span className={styles.metricValue}>{agent.totalIssues}</span>
          <span className={styles.metricLabel}>전체</span>
        </div>
        <div className={styles.metric}>
          <span className={styles.metricValue}>{agent.completedIssues}</span>
          <span className={styles.metricLabel}>완료</span>
        </div>
        <div className={styles.metric}>
          <span className={styles.metricValue}>{agent.inProgressIssues}</span>
          <span className={styles.metricLabel}>진행중</span>
        </div>
        <div className={styles.metric}>
          <span className={styles.metricValue}>{agent.completionRate}%</span>
          <span className={styles.metricLabel}>완료율</span>
        </div>
        <div className={styles.metric}>
          <span className={styles.metricValue}>{agent.avgCompletionTimeMinutes}분</span>
          <span className={styles.metricLabel}>평균 시간</span>
        </div>
      </div>
      <div className={styles.progressBar}>
        <div
          className={styles.progressFill}
          style={{ width: `${agent.completionRate}%` }}
        />
      </div>
    </div>
  );
}
