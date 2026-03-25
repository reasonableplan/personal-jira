import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const root = resolve(__dirname, '../..');

describe('Deployment configuration', () => {
  it('Dockerfile uses multi-stage build', () => {
    const content = readFileSync(resolve(root, 'Dockerfile'), 'utf-8');
    expect(content).toContain('node:20-alpine');
    expect(content).toContain('nginx:alpine');
    expect(content).toContain('npm run build');
  });

  it('nginx.conf has SPA fallback', () => {
    const content = readFileSync(resolve(root, 'nginx.conf'), 'utf-8');
    expect(content).toContain('try_files');
    expect(content).toContain('/index.html');
  });

  it('nginx.conf has API reverse proxy', () => {
    const content = readFileSync(resolve(root, 'nginx.conf'), 'utf-8');
    expect(content).toContain('/api');
    expect(content).toContain('backend:8000');
  });

  it('.dockerignore excludes node_modules', () => {
    const content = readFileSync(resolve(root, '.dockerignore'), 'utf-8');
    expect(content).toContain('node_modules');
  });
});
