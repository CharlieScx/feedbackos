import { isApiErrorResponse, type ApiErrorCode, type components } from "@feedbackos/contracts";

import { apiClient } from "./api-client";

export type Credentials = components["schemas"]["Credentials"];
export type CurrentUser = components["schemas"]["CurrentUser"];

export class RequestError extends Error {
  constructor(public readonly code: ApiErrorCode) {
    super(code);
  }
}

function requestError(result: { error?: unknown; response: Response }) {
  if (isApiErrorResponse(result.error)) return new RequestError(result.error.error.code);
  if (result.response.status === 401) return new RequestError("authentication_failed");
  if (result.response.status === 404) return new RequestError("resource_not_found");
  return new RequestError("internal_error");
}

function payload<T>(result: { data?: T; error?: unknown; response: Response }): T {
  if (!result.response.ok || result.data === undefined) throw requestError(result);
  return result.data;
}

export function hasErrorCode(error: unknown, code: ApiErrorCode) {
  return error instanceof RequestError && error.code === code;
}

export function failureMessage(error: unknown, fallback: string) {
  if (hasErrorCode(error, "authentication_failed")) return "登录已失效，请重新登录。";
  if (hasErrorCode(error, "resource_not_found")) return "资源不存在或你没有访问权限。";
  if (hasErrorCode(error, "request_invalid")) return "请检查输入后重试。";
  if (hasErrorCode(error, "access_denied")) return "请求被拒绝，请从本站页面重试。";
  return fallback;
}

export async function getSession(signal: AbortSignal): Promise<CurrentUser | null> {
  const result = await apiClient.GET("/auth/me", { signal, cache: "no-store" });
  if (result.response.status === 401) return null;
  return payload(result).data;
}

export async function authenticate(mode: "login" | "register", body: Credentials) {
  const result = mode === "login"
    ? await apiClient.POST("/auth/login", { body })
    : await apiClient.POST("/auth/register", { body });
  return payload(result).data;
}

export async function logout() {
  const result = await apiClient.POST("/auth/logout");
  if (!result.response.ok) throw requestError(result);
}

export async function listWorkspaces(page: number, signal: AbortSignal) {
  return payload(await apiClient.GET("/workspaces", { params: { query: { page } }, signal }));
}

export async function getWorkspace(workspaceId: string, signal: AbortSignal) {
  return payload(await apiClient.GET("/workspaces/{workspace_id}", {
    params: { path: { workspace_id: workspaceId } }, signal,
  })).data;
}

export async function createWorkspace(name: string) {
  return payload(await apiClient.POST("/workspaces", { body: { name } })).data;
}

export async function listProjects(workspaceId: string, page: number, signal: AbortSignal) {
  return payload(await apiClient.GET("/workspaces/{workspace_id}/projects", {
    params: { path: { workspace_id: workspaceId }, query: { page } }, signal,
  }));
}

export async function createProject(workspaceId: string, name: string) {
  return payload(await apiClient.POST("/workspaces/{workspace_id}/projects", {
    params: { path: { workspace_id: workspaceId } }, body: { name },
  })).data;
}

export async function getProject(workspaceId: string, projectId: string, signal: AbortSignal) {
  return payload(await apiClient.GET("/workspaces/{workspace_id}/projects/{project_id}", {
    params: { path: { workspace_id: workspaceId, project_id: projectId } }, signal,
  })).data;
}
