import { Card } from "@/components/ui/Card";
import { CampaignStatusBadge } from "@/components/campaigns/CampaignStatusBadge";
import type { Campaign } from "@/lib/types";

export function StepInfo({ campaign }: { campaign: Campaign }) {
  const created = new Date(campaign.created_at).toLocaleString();
  const updated = new Date(campaign.updated_at).toLocaleString();

  return (
    <Card>
      <h2 className="mb-4 text-base font-semibold text-gray-900">
        Campaign Information
      </h2>
      <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-gray-500">
            Name
          </dt>
          <dd className="mt-1 text-sm text-gray-900">{campaign.name}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-gray-500">
            Status
          </dt>
          <dd className="mt-1">
            <CampaignStatusBadge status={campaign.status} />
          </dd>
        </div>
        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-gray-500">
            Budget
          </dt>
          <dd className="mt-1 text-sm text-gray-900">
            {campaign.budget.currency}{" "}
            {Number(campaign.budget.amount).toLocaleString()}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-medium uppercase tracking-wide text-gray-500">
            Created
          </dt>
          <dd className="mt-1 text-sm text-gray-900">{created}</dd>
        </div>
        <div className="sm:col-span-2">
          <dt className="text-xs font-medium uppercase tracking-wide text-gray-500">
            Last Updated
          </dt>
          <dd className="mt-1 text-sm text-gray-900">{updated}</dd>
        </div>
      </dl>
    </Card>
  );
}
