"use client";

import { Alert, Button, Form, Input, Typography } from "antd";

import { appRoutes } from "@/config/routes";

import styles from "./page.module.css";

const { Paragraph, Text, Title } = Typography;

export default function LoginPage() {
  return (
    <main className={styles.page}>
      <section className={styles.card} aria-labelledby="login-title">
        <div className={styles.brand}>
          <span className={styles.brandMark} aria-hidden="true" />
          <Text strong>FeedbackOS</Text>
        </div>

        <div className={styles.intro}>
          <Text type="secondary">反馈决策工作台</Text>
          <Title id="login-title" level={1}>
            登录你的工作空间
          </Title>
          <Paragraph type="secondary">
            从原始反馈证据出发，建立可追溯的产品决策。
          </Paragraph>
        </div>

        <Alert
          showIcon
          type="info"
          title="当前为认证页面骨架"
          description="真实注册、登录和会话恢复将在后续认证任务中接入。"
        />

        <Form className={styles.form} layout="vertical" requiredMark={false}>
          <Form.Item label="邮箱" name="email">
            <Input
              autoComplete="email"
              inputMode="email"
              placeholder="name@company.com"
            />
          </Form.Item>
          <Form.Item label="密码" name="password">
            <Input.Password
              autoComplete="current-password"
              placeholder="输入密码"
            />
          </Form.Item>
          <Button block type="primary" href={appRoutes.workspaces}>
            查看工作空间骨架
          </Button>
        </Form>

        <Paragraph className={styles.footer} type="secondary">
          注册功能将在后续认证任务中接入。
        </Paragraph>
      </section>
    </main>
  );
}
