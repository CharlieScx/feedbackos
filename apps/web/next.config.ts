import type { NextConfig } from "next";

import { createApiProxyRewrite } from "./src/config/api-proxy";

const nextConfig: NextConfig = {
  agentRules: false,
  reactStrictMode: true,
  async rewrites() {
    return [createApiProxyRewrite(process.env.FEEDBACKOS_API_ORIGIN)];
  },
};

export default nextConfig;
