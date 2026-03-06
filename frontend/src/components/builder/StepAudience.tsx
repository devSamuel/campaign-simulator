"use client";

import { Card } from "@/components/ui/Card";
import type { Campaign } from "@/lib/types";

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs font-medium text-gray-500 mb-0.5">{label}</p>
      <p className="text-sm text-gray-900">{value || "—"}</p>
    </div>
  );
}

export function StepAudience({ campaign }: { campaign: Campaign }) {
  const seg = campaign.audience_segment;

  if (!seg) {
    return (
      <Card>
        <p className="text-sm text-gray-400">No audience segment defined.</p>
      </Card>
    );
  }

  return (
    <Card>
      <h2 className="mb-4 text-base font-semibold text-gray-900">Audience Segment</h2>
      <div className="flex flex-col gap-4">
        <Field label="Segment name" value={seg.name} />
        <div className="flex gap-6">
          <Field label="Min age" value={String(seg.age_min)} />
          <Field label="Max age" value={String(seg.age_max)} />
        </div>
        <Field label="Locations" value={seg.locations.join(", ")} />
        <Field label="Interests" value={seg.interests.join(", ")} />
        <Field label="Device types" value={seg.device_types.join(", ")} />
      </div>
    </Card>
  );
}
