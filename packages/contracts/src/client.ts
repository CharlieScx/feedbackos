import createClient, { type ClientOptions } from "openapi-fetch";

import type { paths } from "./schema";

export type ApiClientOptions = Pick<ClientOptions, "baseUrl" | "fetch">;

export function createApiClient(options: ApiClientOptions = {}) {
  return createClient<paths>({
    ...options,
    baseUrl: options.baseUrl ?? "/api",
    credentials: "include",
  });
}

export type ApiClient = ReturnType<typeof createApiClient>;
