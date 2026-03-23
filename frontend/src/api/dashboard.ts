import type { DashboardData } from '@/types/dashboard';

const API_BASE = '/api/v1';

export async function fetchDashboardData(): Promise<DashboardData> {
  const response = await fetch(`${API_BASE}/dashboard`);
  if (!response.ok) {
    throw new Error(`Dashboard API error: ${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<DashboardData>;
}
