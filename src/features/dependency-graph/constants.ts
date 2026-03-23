export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const ENDPOINTS = {
  DEPENDENCY_GRAPH: "/api/v1/issues/dependency-graph",
} as const;

export const STATUS_COLORS: Record<string, string> = {
  BACKLOG: "#94a3b8",
  READY: "#3b82f6",
  IN_PROGRESS: "#f59e0b",
  IN_REVIEW: "#8b5cf6",
  BLOCKED: "#ef4444",
  DONE: "#22c55e",
  CANCELLED: "#6b7280",
} as const;

export const PRIORITY_COLORS: Record<string, string> = {
  CRITICAL: "#dc2626",
  HIGH: "#f97316",
  MEDIUM: "#eab308",
  LOW: "#6b7280",
} as const;

export const GRAPH_LAYOUT = {
  NODE_WIDTH: 240,
  NODE_HEIGHT: 80,
  HORIZONTAL_GAP: 80,
  VERTICAL_GAP: 60,
} as const;

export const EDGE_STYLE = {
  strokeWidth: 2,
  stroke: "#94a3b8",
} as const;
