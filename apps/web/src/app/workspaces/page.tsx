"use client";

import { Alert, Button, Card, Tag, Typography } from "antd";

import { AppShell } from "@/components/app-shell/app-shell";
import { appRoutes } from "@/config/routes";

const { Paragraph, Title } = Typography;

export default function WorkspacesPage() {
  return (
    <AppShell activeSection="workspaces">
      <div className="flex flex-wrap items-center justify-between gap-md">
        <div className="space-y-xs">
          <Title className="!m-none" level={1}>
            工作空间
          </Title>
          <Paragraph className="!m-none" type="secondary">
            选择一个项目，继续进入反馈文件导入流程。
          </Paragraph>
        </div>
        <Button type="primary" disabled>
          创建工作空间（后续接入）
        </Button>
      </div>

      <Alert
        className="mb-xl mt-lg"
        showIcon
        type="info"
        title="这里展示的是路由和租户壳层"
        description="示例名称不代表真实数据；工作空间与项目 API 将在后续任务接入。"
      />

      <section aria-labelledby="workspace-heading">
        <div className="mb-md flex flex-wrap items-center justify-between gap-md">
          <Title className="!m-none" id="workspace-heading" level={2}>
            示例工作空间
          </Title>
          <Tag color="success">界面可浏览</Tag>
        </div>

        <div className="grid grid-cols-[repeat(auto-fit,minmax(min(100%,calc(var(--fo-padding-xl)*10)),1fr))] gap-lg">
          <Card title="产品体验团队" extra={<Tag>Owner</Tag>}>
            <Title level={3}>客服反馈项目</Title>
            <Paragraph type="secondary">
              用于检查项目级导航、导入入口和后续租户边界。
            </Paragraph>
            <Button
              type="primary"
              href={appRoutes.projectImport(
                "demo-workspace",
                "demo-project",
              )}
            >
              打开项目导入页
            </Button>
          </Card>
        </div>
      </section>
    </AppShell>
  );
}
