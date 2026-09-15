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
});
