import type { ReactNode } from "react";

import { SessionBoundary } from "@/components/session-boundary";

export default function WorkspacesLayout({ children }: { children: ReactNode }) {
  return <SessionBoundary>{children}</SessionBoundary>;
}
