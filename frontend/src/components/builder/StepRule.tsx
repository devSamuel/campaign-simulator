"use client";

import { Card } from "@/components/ui/Card";
import type { Campaign } from "@/lib/types";

const METRIC_LABELS: Record<string, string> = {
  ROAS: "ROAS — Return on Ad Spend",
  CTR: "CTR — Click-through Rate",
  CPC: "CPC — Cost per Click",
  CPM: "CPM — Cost per Mille",
  CPA: "CPA — Cost per Acquisition",
};

const OPERATOR_LABELS: Record<string, string> = {
  LT: "Less than (<)",
  GT: "Greater than (>)",
  LTE: "Less than or equal (≤)",
  GTE: "Greater than or equal (≥)",
  EQ: "Equal to (=)",
};

const ACTION_LABELS: Record<string, string> = {
  PAUSE_CAMPAIGN: "Pause Campaign",
  REDUCE_BUDGET: "Reduce Budget by 20%",
  SEND_ALERT: "Send Alert",
};

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-medium text-gray-500 mb-0.5">{label}</p>
      <p className="text-sm text-gray-900">{value || "—"}</p>
    </div>
  );
}

export function StepRule({ campaign }: { campaign: Campaign }) {
  const rule = campaign.rule;

  if (!rule) {
    return (
      <Card>
        <p className="text-sm text-gray-400">No performance rule defined.</p>
      </Card>
    );
  }

  return (
    <Card>
      <h2 className="mb-4 text-base font-semibold text-gray-900">Performance Rule</h2>
      <div className="flex flex-col gap-4">
        <Field label="Metric" value={METRIC_LABELS[rule.metric] ?? rule.metric} />
        <div className="flex gap-6">
          <Field label="Operator" value={OPERATOR_LABELS[rule.operator] ?? rule.operator} />
          <Field label="Threshold" value={String(rule.threshold)} />
        </div>
        <Field label="Action" value={ACTION_LABELS[rule.action] ?? rule.action} />
        {rule.description && (
          <p className="rounded-md bg-indigo-50 px-3 py-2 text-sm text-indigo-700">
            {rule.description}
          </p>
        )}
      </div>
    </Card>
  );
}
