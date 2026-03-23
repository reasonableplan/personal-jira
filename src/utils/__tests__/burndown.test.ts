import { describe, it, expect } from 'vitest';
import {
  generateIdealLine,
  calcCompletionRate,
  calcVelocity,
  isSprintActive,
} from '../burndown';

describe('generateIdealLine', () => {
  it('generates linear ideal burndown', () => {
    const result = generateIdealLine(40, 5);
    expect(result).toEqual([40, 30, 20, 10, 0]);
  });

  it('handles single day sprint', () => {
    const result = generateIdealLine(10, 1);
    expect(result).toEqual([0]);
  });

  it('handles zero total points', () => {
    const result = generateIdealLine(0, 5);
    expect(result).toEqual([0, 0, 0, 0, 0]);
  });

  it('handles fractional decrements', () => {
    const result = generateIdealLine(10, 4);
    expect(result[0]).toBeCloseTo(10);
    expect(result[3]).toBeCloseTo(0);
  });
});

describe('calcCompletionRate', () => {
  it('returns 100% when all points done', () => {
    expect(calcCompletionRate(40, 0)).toBe(100);
  });

  it('returns 0% when no points done', () => {
    expect(calcCompletionRate(40, 40)).toBe(0);
  });

  it('returns correct percentage', () => {
    expect(calcCompletionRate(40, 10)).toBe(75);
  });

  it('returns 0 when total is zero', () => {
    expect(calcCompletionRate(0, 0)).toBe(0);
  });
});

describe('calcVelocity', () => {
  it('calculates points per day', () => {
    expect(calcVelocity(20, 5)).toBe(4);
  });

  it('returns 0 for zero days', () => {
    expect(calcVelocity(20, 0)).toBe(0);
  });
});

describe('isSprintActive', () => {
  it('returns true when today is within range', () => {
    const today = new Date('2026-03-07');
    expect(isSprintActive('2026-03-01', '2026-03-14', today)).toBe(true);
  });

  it('returns false when today is before start', () => {
    const today = new Date('2026-02-28');
    expect(isSprintActive('2026-03-01', '2026-03-14', today)).toBe(false);
  });

  it('returns false when today is after end', () => {
    const today = new Date('2026-03-15');
    expect(isSprintActive('2026-03-01', '2026-03-14', today)).toBe(false);
  });

  it('returns true on start date', () => {
    const today = new Date('2026-03-01');
    expect(isSprintActive('2026-03-01', '2026-03-14', today)).toBe(true);
  });

  it('returns true on end date', () => {
    const today = new Date('2026-03-14');
    expect(isSprintActive('2026-03-01', '2026-03-14', today)).toBe(true);
  });
});
