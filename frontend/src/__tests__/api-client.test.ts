import { describe, it, expect } from 'vitest';
import { API_BASE_URL } from '@/api/client';

describe('API Client', () => {
  it('exports base URL', () => {
    expect(API_BASE_URL).toBe('/api');
  });
});
