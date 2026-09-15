import { describe, expect, it } from "vitest";

import { appRoutes } from "./routes";

describe("appRoutes", () => {
  it("builds the project import route without leaking raw path segments", () => {
    expect(appRoutes.projectImport("team / east", "voice/2026")).toBe(
      "/workspaces/team%20%2F%20east/projects/voice%2F2026/imports/new",
    );
  });
});
