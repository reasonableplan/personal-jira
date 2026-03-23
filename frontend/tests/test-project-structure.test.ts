import { describe, it, expect } from 'vitest';
import { existsSync } from 'fs';
import { resolve } from 'path';

const ROOT = resolve(__dirname, '..');

const REQUIRED_DIRS = [
  'src',
  'src/components',
  'src/pages',
  'src/stores',
  'src/api',
  'src/types',
  'tests',
];

const REQUIRED_FILES = [
  'package.json',
  'tsconfig.json',
  'tsconfig.app.json',
  'tsconfig.node.json',
  'vite.config.ts',
  'tailwind.config.ts',
  'postcss.config.js',
  'index.html',
  '.gitignore',
  'src/main.tsx',
  'src/App.tsx',
  'src/index.css',
  'src/vite-env.d.ts',
];

describe('Project Structure', () => {
  it.each(REQUIRED_DIRS)('directory exists: %s', (dir) => {
    expect(existsSync(resolve(ROOT, dir))).toBe(true);
  });

  it.each(REQUIRED_FILES)('file exists: %s', (file) => {
    expect(existsSync(resolve(ROOT, file))).toBe(true);
  });
});

describe('Package Configuration', () => {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const pkg = require(resolve(ROOT, 'package.json'));

  it('has correct project name', () => {
    expect(pkg.name).toBe('personal-jira-frontend');
  });

  it('uses react 19', () => {
    expect(pkg.dependencies.react).toMatch(/^\^19\./);
  });

  it('uses react-dom 19', () => {
    expect(pkg.dependencies['react-dom']).toMatch(/^\^19\./);
  });

  it('has tailwindcss dependency', () => {
    expect(pkg.devDependencies.tailwindcss).toBeDefined();
  });

  it('has vitest dependency', () => {
    expect(pkg.devDependencies.vitest).toBeDefined();
  });

  it('has typescript dependency', () => {
    expect(pkg.devDependencies.typescript).toBeDefined();
  });
});

describe('Tailwind CSS', () => {
  it('index.css contains tailwind directives', async () => {
    const { readFileSync } = await import('fs');
    const css = readFileSync(resolve(ROOT, 'src/index.css'), 'utf-8');
    expect(css).toContain('@tailwind base');
    expect(css).toContain('@tailwind components');
    expect(css).toContain('@tailwind utilities');
  });
});
