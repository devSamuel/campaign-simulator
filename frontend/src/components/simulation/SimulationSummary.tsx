import { clsx } from "clsx";
import type { SSECompletedPayload } from "@/lib/types";

export function SimulationSummary({ summary }: { summary: SSECompletedPayload }) {
  const triggered = summary.triggered;

  return (
    <div
      className={clsx(
        "rounded-lg border p-5",
        triggered
          ? "border-amber-200 bg-amber-50"
          : "border-green-200 bg-green-50",
      )}
    >
      <h3
        className={clsx(
          "mb-3 text-base font-semibold",
          triggered ? "text-amber-800" : "text-green-800",
        )}
      >
        {triggered ? "⚠️ Rule Triggered" : "✅ Simulation Complete"}
      </h3>

      <dl className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-3">
        <div>
          <dt className="font-medium text-gray-600">Final Status</dt>
          <dd className="mt-0.5 font-semibold text-gray-900">
            {summary.final_status}
          </dd>
        </div>
        <div>
          <dt className="font-medium text-gray-600">Rule Triggered</dt>
          <dd className="mt-0.5 font-semibold text-gray-900">
            {triggered ? "Yes" : "No"}
          </dd>
        </div>
        {triggered && summary.triggered_at_step !== null && (
          <div>
            <dt className="font-medium text-gray-600">Triggered at</dt>
            <dd className="mt-0.5 font-semibold text-gray-900">
              Step {summary.triggered_at_step} (Hour{" "}
              {summary.triggered_at_step})
            </dd>
          </div>
        )}
      </dl>
    </div>
  );
}
