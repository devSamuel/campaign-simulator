import { useMutation, useQueryClient } from "@tanstack/react-query";
import { runSimulation } from "@/lib/api";
import { campaignKeys } from "@/lib/queryKeys";

export function useRunSimulation(campaignId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => runSimulation(campaignId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: campaignKeys.detail(campaignId) });
    },
  });
}
