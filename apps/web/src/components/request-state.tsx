"use client";

import { Alert, Button, Spin } from "antd";
import { useEffect, useRef, useState } from "react";

import { appRoutes } from "@/config/routes";
import { failureMessage, hasErrorCode } from "@/config/workspace-api";

type LoadState<T> =
  | { status: "loading" }
  | { status: "ready"; data: T }
  | { status: "error"; error: unknown };

const loading = { status: "loading" } as const;

export function useLoad<T>(load: (signal: AbortSignal) => Promise<T>) {
  const [attempt, setAttempt] = useState(0);
  const [result, setResult] = useState<{
    load: typeof load; attempt: number; state: LoadState<T>;
  }>();

  useEffect(() => {
    const controller = new AbortController();
    void load(controller.signal).then(
      (data) => {
        if (!controller.signal.aborted) setResult({ load, attempt, state: { status: "ready", data } });
      },
      (error: unknown) => {
        if (!controller.signal.aborted) setResult({ load, attempt, state: { status: "error", error } });
      },
    );
    return () => controller.abort();
  }, [attempt, load]);

  return {
    state: result?.load === load && result.attempt === attempt ? result.state : loading,
    retry: () => setAttempt((previous) => previous + 1),
  };
}

export function LoadingState({ label }: { label: string }) {
  return <div className="flex items-center gap-sm py-lg" role="status"><Spin size="small" />{label}</div>;
}

export function useAction() {
  const active = useRef(false);
  const [pending, setPending] = useState(false);
  const [failure, setFailure] = useState<{ error: unknown }>();

  async function run(action: () => Promise<void>) {
    if (active.current) return;
    active.current = true;
    setPending(true);
    setFailure(undefined);
    try {
      await action();
    } catch (error) {
      setFailure({ error });
    } finally {
      active.current = false;
      setPending(false);
    }
  }

  return { pending, failure, run };
}

export function LoadFailure({ error, retry, fallback }: {
  error: unknown; retry: () => void; fallback: string;
}) {
  const expired = hasErrorCode(error, "authentication_failed");
  const missing = hasErrorCode(error, "resource_not_found");
  return (
    <Alert
      showIcon type="error" title={failureMessage(error, fallback)}
      action={expired ? <Button href={appRoutes.login}>重新登录</Button> : missing
        ? <Button href={appRoutes.workspaces}>返回工作空间</Button>
        : <Button autoInsertSpace={false} onClick={retry}>重试</Button>}
    />
  );
}
