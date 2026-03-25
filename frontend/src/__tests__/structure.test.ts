import { describe, it, expect } from 'vitest';
import { existsSync } from 'fs';
import { resolve } from 'path';

const root = resolve(__dirname, '..');

describe('Frontend project structure', () => {
  const dirs = ['components', 'pages', 'hooks', 'lib', 'types', 'api'];

  dirs.forEach((dir) => {
    it(`src/${dir}/ directory exists`, () => {
      expect(existsSync(resolve(root, dir))).toBe(true);
    });
  });

  it('types/index.ts exports API types', async () => {
    const types = await import('@/types');
    expect(types).toBeDefined();
  });

  it('api/client.ts exports apiClient', async () => {
    const mod = await import('@/api/client');
    expect(mod.apiClient).toBeDefined();
  });

  it('lib/utils.ts exports cn', async () => {
    const mod = await import('@/lib/utils');
    expect(mod.cn).toBeDefined();
  });
});
