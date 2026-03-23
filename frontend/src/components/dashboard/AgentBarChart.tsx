import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { AgentStats } from '@/types/dashboard';
import styles from './Dashboard.module.css';

const BAR_COMPLETED_COLOR = '#34d399';
const BAR_IN_PROGRESS_COLOR = '#fbbf24';

interface AgentBarChartProps {
  agents: AgentStats[];
}

export function AgentBarChart({ agents }: AgentBarChartProps) {
  return (
    <div className={styles.widget}>
      <h3 className={styles.widgetTitle}>에이전트별 이슈 현황</h3>
      {agents.length === 0 ? (
        <p className={styles.emptyMessage}>데이터가 없습니다</p>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={agents} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Legend />
            <Bar dataKey="completedIssues" name="완료" fill={BAR_COMPLETED_COLOR} radius={[4, 4, 0, 0]} />
            <Bar dataKey="inProgressIssues" name="진행중" fill={BAR_IN_PROGRESS_COLOR} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
