import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ReferenceLine,
} from 'recharts';
import type { BurndownChartProps } from '../../types/burndown';
import { isSprintActive } from '../../utils/burndown';

const IDEAL_COLOR = '#94a3b8';
const ACTUAL_COLOR = '#3b82f6';
const TODAY_COLOR = '#ef4444';
const DEFAULT_HEIGHT = 400;

export const BurndownChart: React.FC<BurndownChartProps> = ({ data, height = DEFAULT_HEIGHT }) => {
  const { sprintName, startDate, endDate, totalPoints, points } = data;
  const today = new Date();
  const todayStr = today.toISOString().slice(0, 10);
  const showToday = isSprintActive(startDate, endDate, today);

  if (points.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-slate-200 bg-white p-8">
        <h3 className="text-lg font-semibold text-slate-700">{sprintName}</h3>
        <p className="mt-2 text-sm text-slate-400">데이터가 없습니다</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-700">{sprintName}</h3>
          <p className="text-sm text-slate-400">{startDate} → {endDate}</p>
        </div>
        <span className="rounded-full bg-blue-50 px-3 py-1 text-sm font-medium text-blue-600">
          {totalPoints} 포인트
        </span>
      </div>

      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={points} margin={{ top: 8, right: 24, bottom: 8, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12, fill: '#64748b' }}
            tickFormatter={(v: string) => v.slice(5)}
          />
          <YAxis
            tick={{ fontSize: 12, fill: '#64748b' }}
            domain={[0, totalPoints]}
            allowDataOverflow={false}
          />
          <Tooltip
            contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0' }}
            labelFormatter={(label: string) => `날짜: ${label}`}
          />
          <Legend />
          <Line
            type="linear"
            dataKey="ideal"
            name="이상선"
            stroke={IDEAL_COLOR}
            strokeWidth={2}
            strokeDasharray="6 3"
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="actual"
            name="실제선"
            stroke={ACTUAL_COLOR}
            strokeWidth={2}
            dot={{ r: 4, fill: ACTUAL_COLOR }}
            connectNulls
          />
          {showToday && (
            <ReferenceLine
              x={todayStr}
              stroke={TODAY_COLOR}
              strokeDasharray="4 4"
              label="오늘"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
