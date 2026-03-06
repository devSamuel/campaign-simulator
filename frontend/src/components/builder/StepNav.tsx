import { clsx } from "clsx";
import type { Campaign } from "@/lib/types";

const STEPS = [
  { id: 1, label: "Info" },
  { id: 2, label: "Creativities" },
  { id: 3, label: "Audience" },
  { id: 4, label: "Rule" },
  { id: 5, label: "Simulate" },
];

function isStepEnabled(stepId: number, campaign: Campaign): boolean {
  if (stepId <= 4) return true;
  // Step 5 (Simulate) requires a rule and not already simulating
  return campaign.rule !== null && campaign.status !== "SIMULATING";
}

interface Props {
  activeStep: number;
  campaign: Campaign;
  onStepChange: (step: number) => void;
}

export function StepNav({ activeStep, campaign, onStepChange }: Props) {
  return (
    <nav className="flex border-b border-gray-200">
      {STEPS.map((step) => {
        const enabled = isStepEnabled(step.id, campaign);
        const active = activeStep === step.id;
        return (
          <button
            key={step.id}
            disabled={!enabled}
            onClick={() => enabled && onStepChange(step.id)}
            className={clsx(
              "flex-1 border-b-2 px-4 py-3 text-sm font-medium transition-colors",
              active
                ? "border-indigo-600 text-indigo-600"
                : enabled
                  ? "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
                  : "cursor-not-allowed border-transparent text-gray-300",
            )}
          >
            <span className="mr-1.5 inline-flex h-5 w-5 items-center justify-center rounded-full bg-gray-100 text-xs">
              {step.id}
            </span>
            {step.label}
          </button>
        );
      })}
    </nav>
  );
}
