"use client";

import { Card, Empty, Pagination, Typography } from "antd";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useState } from "react";

import { AppShell } from "@/components/app-shell/app-shell";
import { CreateResourceForm } from "@/components/create-resource-form";
import { LoadFailure, LoadingState, useLoad } from "@/components/request-state";
import { appRoutes } from "@/config/routes";
import { createProject, getWorkspace, listProjects } from "@/config/workspace-api";

export default function WorkspacePage() {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const load = useCallback((signal: AbortSignal) => getWorkspace(workspaceId, signal), [workspaceId]);
  const { state, retry } = useLoad(load);

  return (
    <AppShell activeSection="workspaces">
      {state.status === "loading" && <LoadingState label="正在加载工作空间…" />}
      {state.status === "error" && <LoadFailure error={state.error} retry={retry} fallback="工作空间加载失败。" />}
      {state.status === "ready" && <>
        <Typography.Title level={1}>{state.data.name}</Typography.Title>
        <WorkspaceProjects key={workspaceId} workspaceId={workspaceId} />
      </>}
    </AppShell>
  );
}

function WorkspaceProjects({ workspaceId }: { workspaceId: string }) {
  const router = useRouter();
  const [page, setPage] = useState(1);
  const load = useCallback((signal: AbortSignal) => listProjects(workspaceId, page, signal), [workspaceId, page]);
  const { state, retry } = useLoad(load);

  return (
    <div className="grid gap-lg">
      <CreateResourceForm resource="项目" create={async (name) => {
        const project = await createProject(workspaceId, name);
        router.push(appRoutes.projectImport(workspaceId, project.id));
      }} />
      {state.status === "loading" && <LoadingState label="正在加载项目…" />}
      {state.status === "error" && <LoadFailure error={state.error} retry={retry} fallback="项目列表加载失败。" />}
      {state.status === "ready" && <section className="grid gap-md" aria-labelledby="projects-heading">
        <Typography.Title className="!m-none" id="projects-heading" level={2}>项目</Typography.Title>
        {state.data.data.length === 0 ? <Empty description="暂无项目" /> : state.data.data.map((project) => (
          <Card key={project.id} title={project.name}>
            <Link className="text-brand" href={appRoutes.projectImport(workspaceId, project.id)}>打开项目导入页</Link>
          </Card>
        ))}
        <Pagination current={page} pageSize={state.data.pagination.page_size}
          total={state.data.pagination.total} onChange={setPage} showSizeChanger={false} hideOnSinglePage />
      </section>}
    </div>
  );
}
