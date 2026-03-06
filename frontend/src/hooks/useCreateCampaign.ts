import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createCampaign, runSimulation } from "@/lib/api";
import { campaignKeys } from "@/lib/queryKeys";
import type { CreateCampaignBody } from "@/lib/types";

export function useCreateCampaign() {
  const queryClient = useQueryClient();
  const router = useRouter();

  const mutation = useMutation({
    mutationFn: createCampaign,
    onSuccess: (campaign) => {
      queryClient.invalidateQueries({ queryKey: campaignKeys.list() });
      router.push(`/campaigns/${campaign.id}`);
    },
  });

  async function createAndSimulate(body: CreateCampaignBody) {
    const campaign = await createCampaign(body);
    queryClient.invalidateQueries({ queryKey: campaignKeys.list() });
    const sim = await runSimulation(campaign.id);
    router.push(`/campaigns/${campaign.id}/simulate/${sim.job_id}`);
  }

  return { ...mutation, createAndSimulate };
}
