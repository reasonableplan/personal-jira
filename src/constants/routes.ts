export const ROUTES = {
  DASHBOARD: '/',
  BOARD: '/board',
  ISSUE_DETAIL: '/issues/:id',
} as const;

export type RouteKey = keyof typeof ROUTES;
export type RoutePath = (typeof ROUTES)[RouteKey];

export const ROUTE_LABELS: Record<RoutePath, string> = {
  [ROUTES.DASHBOARD]: '대시보드',
  [ROUTES.BOARD]: '보드',
  [ROUTES.ISSUE_DETAIL]: '이슈 상세',
};

export const NAV_ITEMS: { path: string; label: string }[] = [
  { path: ROUTES.DASHBOARD, label: ROUTE_LABELS[ROUTES.DASHBOARD] },
  { path: ROUTES.BOARD, label: ROUTE_LABELS[ROUTES.BOARD] },
];
