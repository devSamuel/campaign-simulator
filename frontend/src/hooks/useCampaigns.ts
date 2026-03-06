import { useQuery } from "@tanstack/react-query";
import { listCampaigns } from "@/lib/api";
import { campaignKeys } from "@/lib/queryKeys";

export function useCampaigns(params?: { limit?: number; offset?: number }) {
  return useQuery({
    queryKey: campaignKeys.list(params),
    queryFn: () => listCampaigns(params),
  });
}
