"use client";

import { Alert, Button, Card, Steps, Tag, Typography } from "antd";
import { useParams } from "next/navigation";

import { AppShell } from "@/components/app-shell/app-shell";

const { Paragraph, Text, Title } = Typography;

export default function ProjectImportPage() {
  const { workspaceId, projectId } = useParams<{
    workspaceId: string;
    projectId: string;
  }>();

  return (
    <AppShell
      activeSection="import"
      workspaceId={workspaceId}
      workspaceName="产品体验团队"
      projectId={projectId}
      projectName="客服反馈项目"
    >
      <div className="flex flex-wrap items-center justify-between gap-md">
        <div>
          <div className="mb-xs flex flex-wrap items-center gap-xs">
            <Tag color="processing">待上传</Tag>
            <Text type="secondary">项目导入</Text>
          </div>
          <Title className="!mb-xs" level={1}>
            导入反馈文件
          </Title>
          <Paragraph className="!mb-xs" type="secondary">
            先上传文件，再检查有限预览，最后确认字段映射。
          </Paragraph>
        </div>
        <Button disabled>查看历史批次（后续接入）</Button>
      </div>

      <Steps
        className="my-xl rounded-panel bg-layout p-lg shadow-header"
        current={0}
        responsive
        items={[
          { title: "上传文件", content: "CSV 或 XLSX" },
          { title: "检查预览", content: "核对表头与样本" },
          { title: "映射字段", content: "正文为必填项" },
        ]}
      />

      <div className="grid grid-cols-[repeat(auto-fit,minmax(min(100%,calc(var(--fo-padding-xl)*10)),1fr))] gap-lg">
        <Card title="上传文件骨架">
          <div className="grid min-h-[calc(var(--fo-padding-xl)*8)] place-items-center rounded-panel border border-dashed border-border-default bg-surface p-xl text-center">
            <Title className="!mb-sm" level={3}>
              拖入反馈文件或从设备选择
            </Title>
            <Paragraph className="!mb-sm" type="secondary">
              文件类型、大小限制和真实上传进度将在 5.1 从 API 获取。
            </Paragraph>
            <Button type="primary" disabled>
              选择文件（后续接入）
            </Button>
          </div>
        </Card>

        <Card title="本轮边界">
          <div className="grid gap-md">
            <Alert
              showIcon
              type="info"
              title="预览不是导入完成"
              description="第二周只确认文件结构与字段映射，不提前生成可分析反馈。"
            />
            <Text>支持类型和大小限制将由 API 返回。</Text>
            <Text>错误提示不会展示或记录原始反馈全文。</Text>
            <Text>所有批次与文件都将继承工作空间权限。</Text>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
