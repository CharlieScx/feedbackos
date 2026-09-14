const DEFAULT_API_ORIGIN = "http://127.0.0.1:8000";

export interface ApiProxyRewrite {
  source: string;
  destination: string;
}

export function createApiProxyRewrite(
  configuredOrigin: string | undefined,
): ApiProxyRewrite {
  const rawOrigin = configuredOrigin?.trim() || DEFAULT_API_ORIGIN;
  let apiUrl: URL;

  try {
    apiUrl = new URL(rawOrigin);
  } catch {
    throw new Error("FEEDBACKOS_API_ORIGIN must be an absolute HTTP(S) origin");
  }

  if (apiUrl.protocol !== "http:" && apiUrl.protocol !== "https:") {
    throw new Error("FEEDBACKOS_API_ORIGIN must use HTTP or HTTPS");
  }
  if (apiUrl.username || apiUrl.password) {
    throw new Error("FEEDBACKOS_API_ORIGIN must not contain credentials");
  }
  if (apiUrl.pathname !== "/" || apiUrl.search || apiUrl.hash) {
    throw new Error("FEEDBACKOS_API_ORIGIN must not contain a path, query, or fragment");
  }

  return {
    source: "/api/:path*",
    destination: `${apiUrl.origin}/:path*`,
  };
}
