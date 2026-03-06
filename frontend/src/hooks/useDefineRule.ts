import { useMutation, useQueryClient } from "@tanstack/react-query";
import { defineRule } from "@/lib/api";
import { campaignKeys } from "@/lib/queryKeys";
import type { DefineRuleBody } from "@/lib/types";

export function useDefineRule(campaignId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: DefineRuleBody) => defineRule(campaignId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: campaignKeys.detail(campaignId) });
    },
  });
}
