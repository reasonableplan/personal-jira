import { describe, it, expect } from "vitest";
import fs from "fs";
import path from "path";

const ROOT = path.resolve(__dirname, "../..");
const SRC = path.resolve(ROOT, "src");

describe("Frontend project structure", () => {
  const requiredDirs = [
    "src/components",
    "src/pages",
    "src/api",
    "src/types",
    "src/hooks",
  ];

  it.each(requiredDirs)("directory %s exists", (dir) => {
    expect(fs.existsSync(path.resolve(ROOT, dir))).toBe(true);
  });

  it("package.json has required scripts", () => {
    const pkg = JSON.parse(
      fs.readFileSync(path.resolve(ROOT, "package.json"), "utf-8")
    );
    expect(pkg.scripts).toHaveProperty("dev");
    expect(pkg.scripts).toHaveProperty("build");
    expect(pkg.scripts).toHaveProperty("preview");
    expect(pkg.scripts).toHaveProperty("test");
  });

  it("vite.config.ts has API proxy for /api", () => {
    const config = fs.readFileSync(
      path.resolve(ROOT, "vite.config.ts"),
      "utf-8"
    );
    expect(config).toContain('"/api"');
    expect(config).toContain("http://localhost:8000");
  });

  it("tsconfig.app.json has @/ path alias", () => {
    const tsconfig = JSON.parse(
      fs.readFileSync(path.resolve(ROOT, "tsconfig.app.json"), "utf-8")
    );
    expect(tsconfig.compilerOptions.paths).toHaveProperty("@/*");
    expect(tsconfig.compilerOptions.paths["@/*"]).toContain("./src/*");
  });

  it("entry point src/main.tsx exists", () => {
    expect(fs.existsSync(path.resolve(SRC, "main.tsx"))).toBe(true);
  });

  it("App.tsx exists", () => {
    expect(fs.existsSync(path.resolve(SRC, "App.tsx"))).toBe(true);
  });
});
