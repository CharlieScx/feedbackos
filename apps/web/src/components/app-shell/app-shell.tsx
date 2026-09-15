import { Tag } from "antd";
import Link from "next/link";
import type { ReactNode } from "react";

import { appRoutes } from "@/config/routes";

import styles from "./app-shell.module.css";

interface AppShellProps {
  children: ReactNode;
  activeSection: "workspaces" | "import";
  workspaceId?: string;
  workspaceName?: string;
  projectId?: string;
  projectName?: string;
}

export function AppShell({
  children,
  activeSection,
  workspaceId,
  workspaceName,
  projectId,
  projectName,
}: Readonly<AppShellProps>) {
  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <Link className={styles.brand} href={appRoutes.workspaces}>
          <span className={styles.brandMark} aria-hidden="true" />
          <strong>FeedbackOS</strong>
        </Link>

        <nav className={styles.navigation} aria-label="主导航">
          <Link
            className={styles.navigationLink}
            data-active={activeSection === "workspaces"}
            href={appRoutes.workspaces}
            aria-current={activeSection === "workspaces" ? "page" : undefined}
          >
            工作空间
          </Link>
          {workspaceId && workspaceName && projectId && projectName ? (
            <Link
              className={styles.navigationLink}
              data-active={activeSection === "import"}
              href={appRoutes.projectImport(workspaceId, projectId)}
              aria-current={activeSection === "import" ? "page" : undefined}
            >
              项目导入
            </Link>
          ) : null}
        </nav>

        <div className={styles.headerActions}>
          <Tag color="processing">开发骨架</Tag>
          <Link className={styles.secondaryLink} href={appRoutes.login}>
            返回登录
          </Link>
        </div>
      </header>

      {workspaceName ? (
        <div className={styles.contextBar} aria-label="当前位置">
          <span>{workspaceName}</span>
          {projectName ? (
            <>
              <span aria-hidden="true">/</span>
              <strong>{projectName}</strong>
            </>
          ) : null}
        </div>
      ) : null}

      <main className={styles.main}>{children}</main>
    </div>
  );
}
