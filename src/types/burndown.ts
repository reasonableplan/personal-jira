export interface BurndownPoint {
  date: string;
  ideal: number;
  actual: number | null;
}

export interface BurndownData {
  sprintName: string;
  startDate: string;
  endDate: string;
  totalPoints: number;
  points: BurndownPoint[];
}

export interface BurndownChartProps {
  data: BurndownData;
  height?: number;
}

export interface UseBurndownDataReturn {
  data: BurndownData | null;
  isLoading: boolean;
  error: string | null;
}
