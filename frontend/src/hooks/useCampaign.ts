import { useQuery } from "@tanstack/react-query";
import { getCampaign } from "@/lib/api";
import { campaignKeys } from "@/lib/queryKeys";

export function useCampaign(id: string) {
  return useQuery({
    queryKey: campaignKeys.detail(id),
    queryFn: () => getCampaign(id),
    enabled: Boolean(id),
  });
}
