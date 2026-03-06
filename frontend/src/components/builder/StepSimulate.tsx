"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { Spinner } from "@/components/ui/Spinner";
import { useRunSimulation } from "@/hooks/useRunSimulation";
import type { Campaign } from "@/lib/types";

export function StepSimulate({ campaign }: { campaign: Campaign }) {
  const router = useRouter();
  const { mutateAsync, isPending, error } = useRunSimulation(campaign.id);

  const canSimulate =
    campaign.rule !== null && campaign.status !== "SIMULATING";

  async function handleRun() {
    const result = await mutateAsync();
    router.push(`/campaigns/${campaign.id}/simulate/${result.job_id}`);
  }

  return (
    <Card>
      <h2 className="mb-2 text-base font-semibold text-gray-900">
        Run Simulation
      </h2>
      <p className="mb-6 text-sm text-gray-500">
        The simulation runs 24 hourly steps, generating synthetic performance
        data and evaluating your rule at each step. Results stream in real time.
      </p>

      {campaign.status === "SIMULATING" && (
        <div className="mb-4 flex items-center gap-3 rounded-md bg-blue-50 px-4 py-3 text-sm text-blue-700">
          <Spinner className="h-4 w-4 text-blue-600" />
          Simulation already in progress…
        </div>
      )}

      {!campaign.rule && (
        <p className="mb-4 text-sm text-amber-600">
          You must define a performance rule (Step 4) before running a
          simulation.
        </p>
      )}

      {campaign.rule && (
        <div className="mb-4 rounded-md bg-gray-50 px-4 py-3 text-sm text-gray-700">
          <span className="font-medium">Active rule:</span>{" "}
          {campaign.rule.description ?? `${campaign.rule.metric} ${campaign.rule.operator} ${campaign.rule.threshold}`}
        </div>
      )}

      {error && <ErrorMessage message={error.message} />}

      <div className="flex justify-end">
        <Button disabled={!canSimulate} loading={isPending} onClick={handleRun}>
          Run Simulation
        </Button>
      </div>
    </Card>
  );
}
