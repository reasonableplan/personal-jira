import { describe, it, expect } from "vitest";
import { existsSync, readFileSync } from "fs";
import { resolve } from "path";

const ROOT = resolve(__dirname, "../..");

const DEPLOYMENT_FILES = [
  "nginx.conf",
  "Dockerfile",
  ".dockerignore",
  ".env.example",
];

const LIB_FILES = ["src/lib/utils.ts"];

describe("Deployment files", () => {
  it.each(DEPLOYMENT_FILES)("%s exists", (file) => {
    expect(existsSync(resolve(ROOT, file))).toBe(true);
  });

  it.each(LIB_FILES)("%s exists", (file) => {
    expect(existsSync(resolve(ROOT, file))).toBe(true);
  });

  it("src/lib directory exists", () => {
    expect(existsSync(resolve(ROOT, "src/lib"))).toBe(true);
  });
});

describe("nginx.conf", () => {
  const content = readFileSync(resolve(ROOT, "nginx.conf"), "utf-8");

  it("has SPA fallback", () => {
    expect(content).toContain("try_files");
    expect(content).toContain("/index.html");
  });

  it("has API reverse proxy to backend:8000", () => {
    expect(content).toContain("/api");
    expect(content).toContain("backend:8000");
  });
});

describe("Dockerfile", () => {
  const content = readFileSync(resolve(ROOT, "Dockerfile"), "utf-8");

  it("uses node:20-alpine build stage", () => {
    expect(content).toContain("node:20-alpine");
  });

  it("uses nginx:alpine final stage", () => {
    expect(content).toContain("nginx:alpine");
  });

  it("is multi-stage build", () => {
    const fromCount = (content.match(/^FROM /gm) || []).length;
    expect(fromCount).toBeGreaterThanOrEqual(2);
  });

  it("copies nginx.conf", () => {
    expect(content).toContain("nginx.conf");
  });
});

describe(".env.example", () => {
  const content = readFileSync(resolve(ROOT, ".env.example"), "utf-8");

  it("has VITE_API_URL", () => {
    expect(content).toContain("VITE_API_URL");
  });
});
