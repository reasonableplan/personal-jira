import { describe, it, expect } from "vitest";
import { existsSync } from "fs";
import { resolve } from "path";

const ROOT = resolve(__dirname, "../..");
const SRC = resolve(ROOT, "src");

const REQUIRED_DIRS = [
  "src/components",
  "src/pages",
  "src/api",
  "src/types",
  "src/hooks",
];

const REQUIRED_FILES = [
  "package.json",
  "vite.config.ts",
  "tsconfig.json",
  "tsconfig.app.json",
  "tsconfig.node.json",
  "postcss.config.js",
  "tailwind.config.js",
  "index.html",
  "src/main.tsx",
  "src/App.tsx",
  "src/index.css",
  "src/vite-env.d.ts",
];

describe("Frontend project structure", () => {
  it.each(REQUIRED_DIRS)("directory %s exists", (dir) => {
    expect(existsSync(resolve(ROOT, dir))).toBe(true);
  });

  it.each(REQUIRED_FILES)("file %s exists", (file) => {
    expect(existsSync(resolve(ROOT, file))).toBe(true);
  });
});

describe("package.json scripts", () => {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const pkg = require(resolve(ROOT, "package.json"));

  it.each(["dev", "build", "preview", "test"])("has %s script", (script) => {
    expect(pkg.scripts[script]).toBeDefined();
  });
});

describe("vite.config.ts proxy", () => {
  it("has API proxy configuration", async () => {
    const { readFileSync } = await import("fs");
    const content = readFileSync(resolve(ROOT, "vite.config.ts"), "utf-8");
    expect(content).toContain("/api");
    expect(content).toContain("http://localhost:8000");
  });
});

describe("tsconfig path alias", () => {
  it("has @/ alias pointing to src/", async () => {
    const { readFileSync } = await import("fs");
    const content = readFileSync(resolve(ROOT, "tsconfig.app.json"), "utf-8");
    expect(content).toContain("@/*");
    expect(content).toContain("src/*");
  });
});
