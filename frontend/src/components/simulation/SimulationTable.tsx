"use client";

import { useEffect, useRef } from "react";
import { SimulationStepRow } from "./SimulationStepRow";
import type { SimulationStep } from "@/lib/types";

interface Props {
  steps: SimulationStep[];
  triggeredAtStep: number | null;
}

export function SimulationTable({ steps, triggeredAtStep }: Props) {
  const bottomRef = useRef<HTMLTableRowElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [steps.length]);

  return (
    <div className="overflow-auto rounded-lg border border-gray-200">
      <table className="min-w-full text-gray-700">
        <thead className="bg-gray-50 text-xs font-semibold uppercase tracking-wide text-gray-500">
          <tr>
            <th className="px-3 py-2 text-center">Hour</th>
            <th className="px-3 py-2 text-right">ROAS</th>
            <th className="px-3 py-2 text-right">CTR</th>
            <th className="px-3 py-2 text-right">CPC</th>
            <th className="px-3 py-2 text-right">CPM</th>
            <th className="px-3 py-2 text-right">CPA</th>
            <th className="px-3 py-2 text-center">Rule</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {steps.map((step) => (
            <SimulationStepRow
              key={step.step}
              step={step}
              isTriggeredStep={step.step === triggeredAtStep}
            />
          ))}
          <tr ref={bottomRef} />
        </tbody>
      </table>
      {steps.length === 0 && (
        <p className="py-8 text-center text-sm text-gray-400">
          Waiting for simulation data…
        </p>
      )}
    </div>
  );
}
