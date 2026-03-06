"use client";

import Link from "next/link";
import { clsx } from "clsx";
import { SimulationChart } from "./SimulationChart";
import { SimulationTable } from "./SimulationTable";
import { SimulationSummary } from "./SimulationSummary";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { Spinner } from "@/components/ui/Spinner";
import { useSimulationStream } from "@/hooks/useSimulationStream";

interface Props {
  campaignId: string;
  jobId: string;
}

export function SimulationView({ campaignId, jobId }: Props) {
  const { steps, completed, summary, error, isConnected } =
    useSimulationStream(campaignId, jobId);

  const statusLabel = error
    ? "Error"
    : completed
      ? "Complete"
      : isConnected
        ? `Streaming… (${steps.length}/24)`
        : "Connecting…";

  const triggeredAtStep = summary?.triggered_at_step ?? null;

  return (
    <div className="flex flex-col gap-6">
      {/* Status bar */}
      <div className="flex items-center gap-2">
        {!completed && !error && (
          <Spinner className="h-4 w-4 text-indigo-500" />
        )}
        <span
          className={clsx(
            "text-sm font-medium",
            error
              ? "text-red-600"
              : completed
                ? "text-green-600"
                : "text-indigo-600",
          )}
        >
          {statusLabel}
        </span>
      </div>

      {error && <ErrorMessage message={error} />}

      {/* Chart */}
      {steps.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h3 className="mb-3 text-sm font-semibold text-gray-700">
            Metrics over time
          </h3>
          <SimulationChart steps={steps} />
        </div>
      )}

      {/* Table */}
      <SimulationTable steps={steps} triggeredAtStep={triggeredAtStep} />

      {/* Summary */}
      {completed && summary && <SimulationSummary summary={summary} />}

      {/* Back link after completion */}
      {completed && (
        <div>
          <Link
            href={`/campaigns/${campaignId}`}
            className="text-sm text-indigo-600 hover:underline"
          >
            ← Back to campaign
          </Link>
        </div>
      )}
    </div>
  );
}
