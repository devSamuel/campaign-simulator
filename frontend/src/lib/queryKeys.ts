export const campaignKeys = {
  all: ["campaigns"] as const,
  list: (params?: { limit?: number; offset?: number }) =>
    [...campaignKeys.all, "list", params] as const,
  detail: (id: string) => [...campaignKeys.all, "detail", id] as const,
  simulation: (campaignId: string, jobId: string) =>
    [...campaignKeys.all, "simulation", campaignId, jobId] as const,
};
