import { describe, it, expect } from 'vitest';
import { apiClient, API_BASE_URL } from '@/api/client';

describe('API client', () => {
  it('API_BASE_URL points to /api', () => {
    expect(API_BASE_URL).toBe('/api');
  });

  it('apiClient has get, post, patch, delete methods', () => {
    expect(typeof apiClient.get).toBe('function');
    expect(typeof apiClient.post).toBe('function');
    expect(typeof apiClient.patch).toBe('function');
    expect(typeof apiClient.delete).toBe('function');
  });
});
