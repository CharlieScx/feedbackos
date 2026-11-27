"use client";

import { Card, Empty, Pagination, Tag, Typography } from "antd";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";

import { AppShell } from "@/components/app-shell/app-shell";
import { CreateResourceForm } from "@/components/create-resource-form";
import { LoadFailure, LoadingState, useLoad } from "@/components/request-state";
import { appRoutes } from "@/config/routes";
import { createWorkspace, listWorkspaces } from "@/config/workspace-api";

export default function WorkspacesPage() {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const load = useCallback((signal: AbortSignal) => listWorkspaces(page, signal), [page]);
  const { state, retry } = useLoad(load);

  return (
    <AppShell activeSection="workspaces">
      <Typography.Title level={1}>工作空间</Typography.Title>
      <div className="grid gap-lg">
        <CreateResourceForm resource="工作空间" create={async (name) => {
          const workspace = await createWorkspace(name);
          router.push(appRoutes.workspace(workspace.id));
        }} />
        {state.status === "loading" && <LoadingState label="正在加载工作空间…" />}
        {state.status === "error" && <LoadFailure error={state.error} retry={retry} fallback="工作空间加载失败。" />}
        {state.status === "ready" && <section className="grid gap-md" aria-labelledby="spaces-heading">
          <Typography.Title id="spaces-heading" className="!m-none" level={2}>我的工作空间</Typography.Title>
          {state.data.data.length === 0 ? <Empty description="暂无工作空间" /> : state.data.data.map((workspace) => (
            <Card key={workspace.id} title={workspace.name}
              extra={<Tag>{workspace.role === "owner" ? "所有者" : "成员"}</Tag>}>
              <Link className="text-brand" href={appRoutes.workspace(workspace.id)}>打开工作空间</Link>
            </Card>
          ))}
          <Pagination current={page} pageSize={state.data.pagination.page_size}
            total={state.data.pagination.total} onChange={setPage} showSizeChanger={false} hideOnSinglePage />
        </section>}
      </div>
    </AppShell>
  );
}
