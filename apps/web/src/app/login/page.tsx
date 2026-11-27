"use client";

import { Alert, Button, Form, Input, Typography } from "antd";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { LoadFailure, LoadingState, useAction, useLoad } from "@/components/request-state";
import { appRoutes } from "@/config/routes";
import { authenticate, failureMessage, getSession, hasErrorCode, type Credentials } from "@/config/workspace-api";

const { Paragraph, Text, Title } = Typography;

export default function LoginPage() {
  const router = useRouter();
  const { state, retry } = useLoad(getSession);
  const signedIn = state.status === "ready" && state.data !== null;

  useEffect(() => {
    if (signedIn) router.replace(appRoutes.workspaces);
  }, [router, signedIn]);

  return (
    <main className="grid min-h-dvh place-items-center bg-canvas p-page">
      <section
        className="w-full max-w-[calc(var(--fo-padding-xl)*14)] rounded-panel bg-layout p-page shadow-panel"
        aria-labelledby="login-title"
      >
        <div className="mb-lg flex items-center gap-sm">
          <span className="h-lg w-lg rounded-mark bg-brand" aria-hidden="true" />
          <Text strong>FeedbackOS</Text>
        </div>
        {state.status === "error" ? (
          <>
            <Title id="login-title" level={1}>登录</Title>
            <LoadFailure error={state.error} retry={retry} fallback="暂时无法检查会话，请重试。" />
          </>
        ) : state.status === "loading" || signedIn ? (
          <>
            <Title id="login-title" level={1}>登录</Title>
            <LoadingState label={signedIn ? "正在进入工作空间…" : "正在检查会话…"} />
          </>
        ) : <AuthForm />}
      </section>
    </main>
  );
}

function AuthForm() {
  const [mode, setMode] = useState<"login" | "register">("login");
  return <CredentialsForm key={mode} mode={mode} toggle={() => setMode(mode === "login" ? "register" : "login")} />;
}

function CredentialsForm({ mode, toggle }: { mode: "login" | "register"; toggle: () => void }) {
  const registering = mode === "register";
  const router = useRouter();
  const { pending, failure, run } = useAction();
  const error = failure?.error;
  const message = hasErrorCode(error, "authentication_failed") ? "邮箱或密码不正确。"
    : hasErrorCode(error, "conflict") ? "此邮箱已注册，请直接登录。"
    : failureMessage(error, "暂时无法提交，请重试。");

  return (
    <>
      <Title id="login-title" level={1}>{registering ? "创建账号" : "登录你的工作空间"}</Title>
      {failure && <Alert showIcon type="error" title={message} />}
      <Form<Credentials>
        className="mt-lg" layout="vertical" requiredMark={false} disabled={pending}
        onFinish={(values) => void run(async () => {
          await authenticate(mode, { email: values.email.trim(), password: values.password });
          router.replace(appRoutes.workspaces);
        })}
      >
        <Form.Item label="邮箱" name="email" rules={[
          { required: true, message: "请输入邮箱。" },
          { type: "email", transform: (value: string | undefined) => value?.trim(), message: "请输入有效邮箱。" },
        ]}>
          <Input autoComplete="email" inputMode="email" />
        </Form.Item>
        <Form.Item label="密码" name="password" extra={registering ? "使用 15–128 个字符。" : undefined} rules={[
          { required: true, message: "请输入密码。" },
          ...(registering ? [{ validator: async (_rule: unknown, value: string | undefined) => {
            if (!value) return;
            const length = Array.from(value.normalize("NFC")).length;
            if (!value.trim() || length < 15 || length > 128) {
              throw new Error("密码需为 15–128 个字符，且不能全为空格。");
            }
          } }] : []),
        ]}>
          <Input.Password autoComplete={registering ? "new-password" : "current-password"} />
        </Form.Item>
        <Button block type="primary" htmlType="submit" loading={pending} autoInsertSpace={false}>
          {registering ? "注册并进入" : "登录"}
        </Button>
      </Form>
      <Paragraph className="!mb-none mt-md text-center" type="secondary">
        <Button type="link" disabled={pending} onClick={toggle}>
          {registering ? "已有账号，去登录" : "没有账号？去注册"}
        </Button>
      </Paragraph>
    </>
  );
}
