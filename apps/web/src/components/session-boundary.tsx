"use client";

import { useRouter } from "next/navigation";
import { createContext, useContext, useEffect, type ReactNode } from "react";

import { appRoutes } from "@/config/routes";
import { getSession, type CurrentUser } from "@/config/workspace-api";

import { LoadFailure, LoadingState, useLoad } from "./request-state";

const SessionContext = createContext<CurrentUser | null>(null);

export function useSession() {
  return useContext(SessionContext);
}

export function SessionBoundary({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { state, retry } = useLoad(getSession);
  const anonymous = state.status === "ready" && state.data === null;

  useEffect(() => {
    if (anonymous) router.replace(appRoutes.login);
  }, [anonymous, router]);

  if (state.status === "ready" && state.data) {
    return <SessionContext.Provider value={state.data}>{children}</SessionContext.Provider>;
  }

  return (
    <main className="mx-auto w-full max-w-[calc(var(--fo-padding-xl)*20)] p-page">
      {state.status === "error"
        ? <LoadFailure error={state.error} retry={retry} fallback="暂时无法恢复会话，请重试。" />
        : <LoadingState label={anonymous ? "正在前往登录页…" : "正在恢复会话…"} />}
    </main>
  );
}
