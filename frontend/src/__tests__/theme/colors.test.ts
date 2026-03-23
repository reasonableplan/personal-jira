import { describe, it, expect } from 'vitest';
import { THEME_COLORS } from '../../theme/colors';

describe('THEME_COLORS', () => {
  it('defines primary color palette', () => {
    expect(THEME_COLORS.primary).toBeDefined();
    expect(THEME_COLORS.primary[500]).toBeDefined();
    expect(THEME_COLORS.primary[50]).toBeDefined();
    expect(THEME_COLORS.primary[900]).toBeDefined();
  });

  it('defines status colors', () => {
    expect(THEME_COLORS.status.success).toBeDefined();
    expect(THEME_COLORS.status.warning).toBeDefined();
    expect(THEME_COLORS.status.error).toBeDefined();
    expect(THEME_COLORS.status.info).toBeDefined();
  });

  it('defines priority colors', () => {
    expect(THEME_COLORS.priority.critical).toBeDefined();
    expect(THEME_COLORS.priority.high).toBeDefined();
    expect(THEME_COLORS.priority.medium).toBeDefined();
    expect(THEME_COLORS.priority.low).toBeDefined();
  });

  it('defines issue status colors', () => {
    expect(THEME_COLORS.issueStatus.backlog).toBeDefined();
    expect(THEME_COLORS.issueStatus.ready).toBeDefined();
    expect(THEME_COLORS.issueStatus.inProgress).toBeDefined();
    expect(THEME_COLORS.issueStatus.inReview).toBeDefined();
    expect(THEME_COLORS.issueStatus.done).toBeDefined();
    expect(THEME_COLORS.issueStatus.closed).toBeDefined();
    expect(THEME_COLORS.issueStatus.cancelled).toBeDefined();
  });

  it('all color values are valid hex strings', () => {
    const hexPattern = /^#[0-9a-fA-F]{6}$/;

    const checkColors = (obj: Record<string, string | Record<string, string>>) => {
      for (const value of Object.values(obj)) {
        if (typeof value === 'string') {
          expect(value).toMatch(hexPattern);
        } else {
          checkColors(value as Record<string, string>);
        }
      }
    };

    checkColors(THEME_COLORS as unknown as Record<string, string | Record<string, string>>);
  });
});
