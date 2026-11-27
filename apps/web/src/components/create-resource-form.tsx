"use client";

import { Alert, Button, Card, Form, Input } from "antd";
import Link from "next/link";

import { appRoutes } from "@/config/routes";
import { failureMessage, hasErrorCode } from "@/config/workspace-api";

import { useAction } from "./request-state";

export function CreateResourceForm({ resource, create }: {
  resource: "工作空间" | "项目"; create: (name: string) => Promise<void>;
}) {
  const { pending, failure, run } = useAction();
  const title = `创建${resource}`;

  return (
    <Card title={title}>
      {failure && <Alert className="mb-md" showIcon type="error"
        title={failureMessage(failure.error, `${title}失败，请重试。`)}
        action={hasErrorCode(failure.error, "authentication_failed")
          ? <Link href={appRoutes.login}>重新登录</Link> : undefined} />}
      <Form<{ name: string }> layout="vertical" requiredMark={false} disabled={pending}
        onFinish={({ name }) => void run(() => create(name.trim()))}>
        <Form.Item name="name" label={`${resource}名称`} rules={[
          { required: true, whitespace: true, message: `请输入${resource}名称。` },
          { validator: async (_rule, value: string | undefined) => {
            if (value && (Array.from(value.trim()).length > 200 || value.includes("\0"))) {
              throw new Error("名称最多 200 个字符，且不能包含空字符。");
            }
          } },
        ]}>
          <Input />
        </Form.Item>
        <Button type="primary" htmlType="submit" loading={pending}>{title}</Button>
      </Form>
    </Card>
  );
}
