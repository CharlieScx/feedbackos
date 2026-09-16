import { Tag } from "antd";
import Link from "next/link";
import type { ReactNode } from "react";

import { appRoutes } from "@/config/routes";

interface AppShellProps {
  children: ReactNode;
  activeSection: "workspaces" | "import";
  workspaceId?: string;
  workspaceName?: string;
  projectId?: string;
  projectName?: string;
}

const navigationLinkClass =
  "rounded-control px-sm py-xs text-muted no-underline";

export function AppShell({
  children,
  activeSection,
  workspaceId,
  workspaceName,
  projectId,
  projectName,
}: Readonly<AppShellProps>) {
  return (
    <div className="min-h-dvh bg-canvas">
      <header className="flex flex-wrap items-center gap-md bg-layout px-page py-md shadow-header">
        <Link
          className="flex items-center gap-sm text-large text-content no-underline"
          href={appRoutes.workspaces}
        >
          <span
            className="h-lg w-lg rounded-mark bg-brand"
            aria-hidden="true"
          />
          <strong>FeedbackOS</strong>
        </Link>

        <nav
          className="flex flex-1 flex-wrap items-center gap-xs"
          aria-label="主导航"
        >
          <Link
            className={`${navigationLinkClass} ${
              activeSection === "workspaces" ? "bg-brand-soft text-brand" : ""
            }`}
            href={appRoutes.workspaces}
            aria-current={activeSection === "workspaces" ? "page" : undefined}
          >
            工作空间
          </Link>
          {workspaceId && workspaceName && projectId && projectName ? (
            <Link
              className={`${navigationLinkClass} ${
                activeSection === "import" ? "bg-brand-soft text-brand" : ""
              }`}
              href={appRoutes.projectImport(workspaceId, projectId)}
              aria-current={activeSection === "import" ? "page" : undefined}
            >
              项目导入
            </Link>
          ) : null}
        </nav>

        <div className="flex items-center gap-sm">
          <Tag color="processing">开发骨架</Tag>
          <Link
            className="rounded-control text-muted no-underline"
            href={appRoutes.login}
          >
            返回登录
          </Link>
        </div>
      </header>

      {workspaceName ? (
        <div
          className="flex items-center gap-xs px-page py-sm text-small text-muted"
          aria-label="当前位置"
        >
          <span>{workspaceName}</span>
          {projectName ? (
            <>
              <span aria-hidden="true">/</span>
              <strong>{projectName}</strong>
            </>
          ) : null}
        </div>
      ) : null}

      <main className="p-page">{children}</main>
    </div>
  );
}
