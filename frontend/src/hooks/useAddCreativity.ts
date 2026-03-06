import { useMutation, useQueryClient } from "@tanstack/react-query";
import { addCreativity } from "@/lib/api";
import { campaignKeys } from "@/lib/queryKeys";
import type { AddCreativityBody } from "@/lib/types";

export function useAddCreativity(campaignId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: AddCreativityBody) => addCreativity(campaignId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: campaignKeys.detail(campaignId) });
    },
  });
}
