import { readdirSync, readFileSync } from "node:fs";
import { extname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const sourceDirectory = fileURLToPath(new URL("../", import.meta.url));
const sourceExtensions = new Set([".css", ".ts", ".tsx"]);

function collectRuntimeSourceFiles(directory: string): string[] {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = join(directory, entry.name);

    if (entry.isDirectory()) {
      return collectRuntimeSourceFiles(path);
    }

    if (
      !sourceExtensions.has(extname(entry.name)) ||
      entry.name.includes(".test.")
    ) {
      return [];
    }

    return [path];
  });
}

describe("theme source contract", () => {
  const runtimeSources = collectRuntimeSourceFiles(sourceDirectory);

  it("does not depend on local skill-package or machine paths", () => {
    const forbiddenPath =
      /\/Users\/|(?:^|[/'"])(?:\.agents|\.codex|\.claude)\/skills\//m;

    for (const path of runtimeSources) {
      expect(readFileSync(path, "utf8"), path).not.toMatch(forbiddenPath);
    }
  });

  it("keeps literal colors inside the authoritative token snapshot", () => {
    const literalColor = /#[0-9a-f]{3,8}\b|(?:rgb|hsl)a?\(/i;

    for (const path of runtimeSources) {
      expect(readFileSync(path, "utf8"), path).not.toMatch(literalColor);
    }
  });

  it("maps semantic Tailwind utilities to runtime theme tokens", () => {
    const globalStyles = readFileSync(
      join(sourceDirectory, "app", "globals.css"),
      "utf8",
    );

    expect(globalStyles).toContain('@import "tailwindcss"');
    expect(globalStyles).toContain("@theme inline");
    expect(globalStyles).toContain(
      "--color-canvas: var(--fo-color-bg-base)",
    );
    expect(globalStyles).toContain("--spacing-page: var(--fo-padding-xl)");
    expect(globalStyles).toContain(
      "--radius-panel: var(--fo-border-radius-lg)",
    );
  });

  it("keeps the migrated UI free from CSS Modules", () => {
    const migratedSources = [
      join(sourceDirectory, "app", "login", "page.tsx"),
      join(sourceDirectory, "app", "workspaces", "page.tsx"),
      join(
        sourceDirectory,
        "app",
        "workspaces",
        "[workspaceId]",
        "projects",
        "[projectId]",
        "imports",
        "new",
        "page.tsx",
      ),
      join(sourceDirectory, "components", "app-shell", "app-shell.tsx"),
    ];

    for (const path of migratedSources) {
      expect(readFileSync(path, "utf8"), path).not.toContain(".module.css");
    }
  });
});
