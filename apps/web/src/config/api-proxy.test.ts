import { describe, expect, it } from "vitest";

import { createApiProxyRewrite } from "./api-proxy";

describe("createApiProxyRewrite", () => {
  it("proxies the browser's same-origin API path to the local API by default", () => {
    expect(createApiProxyRewrite(undefined)).toEqual({
      source: "/api/:path*",
      destination: "http://127.0.0.1:8000/:path*",
    });
  });

  it("normalizes a configured HTTPS origin", () => {
    expect(createApiProxyRewrite(" https://api.feedbackos.example/ ")).toEqual({
      source: "/api/:path*",
      destination: "https://api.feedbackos.example/:path*",
    });
  });

  it.each([
    "ftp://api.feedbackos.example",
    "https://user:secret@api.feedbackos.example",
    "https://api.feedbackos.example/base",
    "https://api.feedbackos.example?target=other",
    "not-a-url",
  ])("rejects unsafe or ambiguous API origin %s", (origin) => {
    expect(() => createApiProxyRewrite(origin)).toThrow(/FEEDBACKOS_API_ORIGIN/);
  });
});
