export const ROUTES = {
  DASHBOARD: '/',
  BOARD: '/board',
  ISSUE_DETAIL: '/issues/:id',
} as const;

export function issueDetailPath(id: string): string {
  return `/issues/${id}`;
}
