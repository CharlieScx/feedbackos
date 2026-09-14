import { describe, expect, it } from "vitest";

import { GET } from "./route";

describe("GET /health", () => {
  it("reports Next.js liveness without a cached response", async () => {
    const response = GET();

    await expect(response.json()).resolves.toEqual({
      service: "feedbackos-web",
      status: "ok",
    });
    expect(response.status).toBe(200);
    expect(response.headers.get("cache-control")).toBe("no-store");
  });
});
