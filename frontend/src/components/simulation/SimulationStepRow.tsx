import { clsx } from "clsx";
import type { SimulationStep } from "@/lib/types";

interface Props {
  step: SimulationStep;
  isTriggeredStep: boolean;
}

function fmt(n: number, decimals = 4): string {
  return n.toFixed(decimals);
}

export function SimulationStepRow({ step, isTriggeredStep }: Props) {
  return (
    <tr
      className={clsx(
        "transition-colors",
        isTriggeredStep
          ? "bg-red-50 font-semibold text-red-700"
          : step.rule_triggered
            ? "bg-amber-50 text-amber-700"
            : "hover:bg-gray-50",
      )}
    >
      <td className="px-3 py-2 text-center text-xs">{step.hour}</td>
      <td className="px-3 py-2 text-right text-xs">{fmt(step.metrics.ROAS, 2)}</td>
      <td className="px-3 py-2 text-right text-xs">
        {(step.metrics.CTR * 100).toFixed(2)}%
      </td>
      <td className="px-3 py-2 text-right text-xs">${fmt(step.metrics.CPC, 2)}</td>
      <td className="px-3 py-2 text-right text-xs">${fmt(step.metrics.CPM, 2)}</td>
      <td className="px-3 py-2 text-right text-xs">${fmt(step.metrics.CPA, 2)}</td>
      <td className="px-3 py-2 text-center text-xs">
        {step.rule_triggered ? (
          <span title={step.rule_description ?? undefined}>
            {isTriggeredStep ? "🔴 Triggered" : "⚠️"}
          </span>
        ) : (
          <span className="text-gray-300">—</span>
        )}
      </td>
    </tr>
  );
}
