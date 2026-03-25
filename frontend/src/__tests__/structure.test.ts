import { describe, it, expect } from 'vitest';
import { existsSync } from 'fs';
import { resolve } from 'path';

const ROOT = resolve(__dirname, '..', '..');
const SRC = resolve(ROOT, 'src');

describe('Frontend project structure', () => {
  const requiredDirs = [
    'src/components',
    'src/pages',
    'src/hooks',
    'src/lib',
    'src/types',
    'src/api',
  ];

  it.each(requiredDirs)('directory %s exists', (dir) => {
    expect(existsSync(resolve(ROOT, dir))).toBe(true);
  });

  const requiredFiles = [
    'src/main.tsx',
    'src/App.tsx',
    'src/index.css',
    'src/lib/utils.ts',
    'src/types/index.ts',
    'src/vite-env.d.ts',
    'index.html',
    'vite.config.ts',
    'tsconfig.json',
    'tsconfig.app.json',
    'tsconfig.node.json',
    'package.json',
    'postcss.config.js',
    'nginx.conf',
    'Dockerfile',
    '.dockerignore',
    '.env.example',
  ];

  it.each(requiredFiles)('file %s exists', (file) => {
    expect(existsSync(resolve(ROOT, file))).toBe(true);
  });
});
