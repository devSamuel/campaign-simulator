import { useQuery } from "@tanstack/react-query";
import { getSimulationResult } from "@/lib/api";
import { campaignKeys } from "@/lib/queryKeys";

export function usePollSimulation(
  campaignId: string,
  jobId: string,
  options?: { enabled?: boolean },
) {
  return useQuery({
    queryKey: campaignKeys.simulation(campaignId, jobId),
    queryFn: () => getSimulationResult(campaignId, jobId),
    enabled: options?.enabled ?? true,
    refetchInterval: (query) => {
      // Stop polling once we have a result
      if (query.state.data) return false;
      return 2000;
    },
    retry: false,
  });
}
