import { describe, it, expect } from "vitest";
import { existsSync, readFileSync } from "fs";
import { resolve } from "path";

const ROOT = resolve(__dirname, "../..");

describe("Docker & nginx configuration", () => {
  it("Dockerfile exists", () => {
    expect(existsSync(resolve(ROOT, "Dockerfile"))).toBe(true);
  });

  it("Dockerfile uses multi-stage build", () => {
    const content = readFileSync(resolve(ROOT, "Dockerfile"), "utf-8");
    expect(content).toContain("node:20-alpine");
    expect(content).toContain("nginx:alpine");
    expect(content).toContain("AS build");
  });

  it(".dockerignore exists", () => {
    expect(existsSync(resolve(ROOT, ".dockerignore"))).toBe(true);
  });

  it(".dockerignore excludes node_modules", () => {
    const content = readFileSync(resolve(ROOT, ".dockerignore"), "utf-8");
    expect(content).toContain("node_modules");
  });

  it("nginx.conf exists", () => {
    expect(existsSync(resolve(ROOT, "nginx.conf"))).toBe(true);
  });

  it("nginx.conf has SPA fallback", () => {
    const content = readFileSync(resolve(ROOT, "nginx.conf"), "utf-8");
    expect(content).toContain("try_files");
    expect(content).toContain("/index.html");
  });

  it("nginx.conf has /api reverse proxy", () => {
    const content = readFileSync(resolve(ROOT, "nginx.conf"), "utf-8");
    expect(content).toContain("/api");
    expect(content).toContain("proxy_pass");
    expect(content).toContain("backend:8000");
  });

  it(".env.example exists", () => {
    expect(existsSync(resolve(ROOT, ".env.example"))).toBe(true);
  });
});

describe("shadcn/ui utilities", () => {
  it("src/lib directory exists", () => {
    expect(existsSync(resolve(ROOT, "src/lib"))).toBe(true);
  });

  it("src/lib/utils.ts exists", () => {
    expect(existsSync(resolve(ROOT, "src/lib/utils.ts"))).toBe(true);
  });

  it("utils.ts exports cn function", () => {
    const content = readFileSync(resolve(ROOT, "src/lib/utils.ts"), "utf-8");
    expect(content).toContain("export function cn");
    expect(content).toContain("clsx");
    expect(content).toContain("twMerge");
  });
});
