import { describe, it, expect } from 'vitest';
import { resolve } from 'path';
import { existsSync } from 'fs';

const root = resolve(__dirname, '../..');
const src = resolve(root, 'src');

describe('Project Structure', () => {
  it('has required config files', () => {
    const configs = [
      'package.json',
      'vite.config.ts',
      'tsconfig.json',
      'tsconfig.app.json',
      'tsconfig.node.json',
      'tailwind.config.js',
      'postcss.config.js',
      'index.html',
      'components.json',
      'nginx.conf',
      'Dockerfile',
      '.dockerignore',
      '.env.example',
    ];
    for (const f of configs) {
      expect(existsSync(resolve(root, f)), `${f} should exist`).toBe(true);
    }
  });

  it('has required src directories', () => {
    const dirs = ['components', 'pages', 'hooks', 'lib', 'types', 'api'];
    for (const d of dirs) {
      expect(existsSync(resolve(src, d)), `src/${d} should exist`).toBe(true);
    }
  });

  it('has entry files', () => {
    expect(existsSync(resolve(src, 'main.tsx'))).toBe(true);
    expect(existsSync(resolve(src, 'App.tsx'))).toBe(true);
    expect(existsSync(resolve(src, 'index.css'))).toBe(true);
  });

  it('has cn utility', () => {
    expect(existsSync(resolve(src, 'lib/utils.ts'))).toBe(true);
  });

  it('has API types matching spec', () => {
    expect(existsSync(resolve(src, 'types/index.ts'))).toBe(true);
  });

  it('has API client', () => {
    expect(existsSync(resolve(src, 'api/client.ts'))).toBe(true);
  });
});
