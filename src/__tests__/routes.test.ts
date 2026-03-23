import { describe, it, expect } from 'vitest';
import { ROUTES, ROUTE_LABELS } from '../constants/routes';

describe('ROUTES', () => {
  it('defines dashboard route', () => {
    expect(ROUTES.DASHBOARD).toBe('/');
  });

  it('defines board route', () => {
    expect(ROUTES.BOARD).toBe('/board');
  });

  it('defines issue detail route', () => {
    expect(ROUTES.ISSUE_DETAIL).toBe('/issues/:id');
  });

  it('has label for every route', () => {
    expect(ROUTE_LABELS[ROUTES.DASHBOARD]).toBe('대시보드');
    expect(ROUTE_LABELS[ROUTES.BOARD]).toBe('보드');
    expect(ROUTE_LABELS[ROUTES.ISSUE_DETAIL]).toBe('이슈 상세');
  });
});
