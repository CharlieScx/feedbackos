export const appRoutes = {
  login: "/login",
  workspaces: "/workspaces",
  workspace(workspaceId: string) {
    return `/workspaces/${encodeURIComponent(workspaceId)}`;
  },
  projectImport(workspaceId: string, projectId: string) {
    return `/workspaces/${encodeURIComponent(workspaceId)}/projects/${encodeURIComponent(projectId)}/imports/new`;
  },
} as const;
