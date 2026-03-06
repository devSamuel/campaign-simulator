import { useMutation, useQueryClient } from "@tanstack/react-query";
import { setAudience } from "@/lib/api";
import { campaignKeys } from "@/lib/queryKeys";
import type { SetAudienceBody } from "@/lib/types";

export function useSetAudience(campaignId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: SetAudienceBody) => setAudience(campaignId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: campaignKeys.detail(campaignId) });
    },
  });
}
