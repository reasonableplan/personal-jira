import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { AgentStatsCard } from '../AgentStatsCard';
import type { AgentStats } from '@/types/dashboard';

const MOCK_AGENT: AgentStats = {
  agentId: 'agent-001',
  name: 'agent-backend',
  totalIssues: 20,
  completedIssues: 15,
  inProgressIssues: 3,
  avgCompletionTimeMinutes: 12.5,
  completionRate: 75,
};

describe('AgentStatsCard', () => {
  it('renders agent name', () => {
    render(<AgentStatsCard agent={MOCK_AGENT} />);
    expect(screen.getByText('agent-backend')).toBeInTheDocument();
  });

  it('displays total issues count', () => {
    render(<AgentStatsCard agent={MOCK_AGENT} />);
    expect(screen.getByText('20')).toBeInTheDocument();
    expect(screen.getByText('전체')).toBeInTheDocument();
  });

  it('displays completed issues count', () => {
    render(<AgentStatsCard agent={MOCK_AGENT} />);
    expect(screen.getByText('15')).toBeInTheDocument();
    expect(screen.getByText('완료')).toBeInTheDocument();
  });

  it('displays in-progress issues count', () => {
    render(<AgentStatsCard agent={MOCK_AGENT} />);
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('진행중')).toBeInTheDocument();
  });

  it('displays completion rate', () => {
    render(<AgentStatsCard agent={MOCK_AGENT} />);
    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('displays average completion time', () => {
    render(<AgentStatsCard agent={MOCK_AGENT} />);
    expect(screen.getByText('12.5분')).toBeInTheDocument();
  });

  it('renders with zero stats', () => {
    const zeroAgent: AgentStats = {
      agentId: 'agent-002',
      name: 'agent-idle',
      totalIssues: 0,
      completedIssues: 0,
      inProgressIssues: 0,
      avgCompletionTimeMinutes: 0,
      completionRate: 0,
    };
    render(<AgentStatsCard agent={zeroAgent} />);
    expect(screen.getByText('agent-idle')).toBeInTheDocument();
    expect(screen.getByText('0%')).toBeInTheDocument();
  });
});
