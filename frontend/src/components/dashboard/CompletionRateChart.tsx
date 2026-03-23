import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import type { StatusCount } from '@/types/dashboard';
import { STATUS_COLORS } from '@/types/dashboard';
import styles from './Dashboard.module.css';

interface CompletionRateChartProps {
  statusCounts: StatusCount[];
  completionRate: number;
}

export function CompletionRateChart({ statusCounts, completionRate }: CompletionRateChartProps) {
  const chartData = statusCounts.filter((s) => s.count > 0);

  return (
    <div className={styles.widget}>
      <h3 className={styles.widgetTitle}>완료율</h3>
      <div className={styles.donutContainer}>
        <div className={styles.donutChart}>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={chartData}
                  dataKey="count"
                  nameKey="status"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={2}
                >
                  {chartData.map((entry) => (
                    <Cell key={entry.status} fill={STATUS_COLORS[entry.status]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className={styles.emptyChart} />
          )}
          <div className={styles.donutCenter}>
            <span className={styles.rateValue}>{completionRate}%</span>
          </div>
        </div>
        <ul className={styles.legend}>
          {statusCounts.map((s) => (
            <li key={s.status} className={styles.legendItem}>
              <span
                className={styles.legendDot}
                style={{ backgroundColor: STATUS_COLORS[s.status] }}
              />
              <span className={styles.legendLabel}>{s.status}</span>
              <span className={styles.legendCount}>{s.count}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
