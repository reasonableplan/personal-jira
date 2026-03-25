import { existsSync } from 'fs';
import { resolve } from 'path';
import { describe, expect, it } from 'vitest';

const ROOT = resolve(__dirname, '../..');
const SRC = resolve(ROOT, 'src');

describe('project structure', () => {
  const requiredRootFiles = [
    'package.json',
    'tsconfig.json',
    'tsconfig.app.json',
    'tsconfig.node.json',
    'vite.config.ts',
    'postcss.config.js',
    'tailwind.config.js',
    'index.html',
    'nginx.conf',
    'Dockerfile',
    '.dockerignore',
    '.env.example',
  ];

  requiredRootFiles.forEach((file) => {
    it(`has ${file}`, () => {
      expect(existsSync(resolve(ROOT, file))).toBe(true);
    });
  });

  const requiredDirs = [
    'components',
    'pages',
    'hooks',
    'lib',
    'types',
    'api',
  ];

  requiredDirs.forEach((dir) => {
    it(`has src/${dir}/ directory`, () => {
      expect(existsSync(resolve(SRC, dir))).toBe(true);
    });
  });

  it('has src/types/index.ts with type exports', () => {
    expect(existsSync(resolve(SRC, 'types/index.ts'))).toBe(true);
  });

  it('has src/lib/utils.ts with cn utility', () => {
    expect(existsSync(resolve(SRC, 'lib/utils.ts'))).toBe(true);
  });
});
