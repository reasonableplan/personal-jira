import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { AgentBarChart } from '../AgentBarChart';
import type { AgentStats } from '@/types/dashboard';

const MOCK_AGENTS: AgentStats[] = [
  {
    agentId: 'agent-001',
    name: 'agent-backend',
    totalIssues: 20,
    completedIssues: 15,
    inProgressIssues: 3,
    avgCompletionTimeMinutes: 12.5,
    completionRate: 75,
  },
  {
    agentId: 'agent-002',
    name: 'agent-frontend',
    totalIssues: 10,
    completedIssues: 8,
    inProgressIssues: 2,
    avgCompletionTimeMinutes: 8.3,
    completionRate: 80,
  },
];

describe('AgentBarChart', () => {
  it('renders the chart title', () => {
    render(<AgentBarChart agents={MOCK_AGENTS} />);
    expect(screen.getByText('에이전트별 이슈 현황')).toBeInTheDocument();
  });

  it('renders with empty agents list', () => {
    render(<AgentBarChart agents={[]} />);
    expect(screen.getByText('에이전트별 이슈 현황')).toBeInTheDocument();
    expect(screen.getByText('데이터가 없습니다')).toBeInTheDocument();
  });

  it('renders chart container', () => {
    const { container } = render(<AgentBarChart agents={MOCK_AGENTS} />);
    expect(container.querySelector('.recharts-responsive-container')).toBeInTheDocument();
  });
});
