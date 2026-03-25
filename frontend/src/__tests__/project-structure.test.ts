import { describe, it, expect } from 'vitest';
import { existsSync } from 'fs';
import { resolve } from 'path';

const root = resolve(__dirname, '../..');
const src = resolve(__dirname, '..');

describe('Project structure', () => {
  const rootFiles = [
    'package.json',
    'vite.config.ts',
    'tsconfig.json',
    'tsconfig.app.json',
    'tsconfig.node.json',
    'postcss.config.js',
    'tailwind.config.js',
    'index.html',
    'Dockerfile',
    'nginx.conf',
    '.dockerignore',
    '.env.example',
    'components.json',
  ];

  rootFiles.forEach((file) => {
    it(`has ${file}`, () => {
      expect(existsSync(resolve(root, file))).toBe(true);
    });
  });

  const srcDirs = ['components', 'pages', 'hooks', 'lib', 'types', 'api'];

  srcDirs.forEach((dir) => {
    it(`has src/${dir} directory`, () => {
      expect(existsSync(resolve(src, dir))).toBe(true);
    });
  });

  it('has src/main.tsx', () => {
    expect(existsSync(resolve(src, 'main.tsx'))).toBe(true);
  });

  it('has src/App.tsx', () => {
    expect(existsSync(resolve(src, 'App.tsx'))).toBe(true);
  });

  it('has src/lib/utils.ts', () => {
    expect(existsSync(resolve(src, 'lib', 'utils.ts'))).toBe(true);
  });

  it('has src/types/index.ts', () => {
    expect(existsSync(resolve(src, 'types', 'index.ts'))).toBe(true);
  });
});
