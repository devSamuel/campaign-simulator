import Link from "next/link";
import { CampaignStatusBadge } from "./CampaignStatusBadge";
import type { CampaignSummary } from "@/lib/types";

export function CampaignCard({ campaign }: { campaign: CampaignSummary }) {
  const date = new Date(campaign.created_at).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  return (
    <Link
      href={`/campaigns/${campaign.id}`}
      className="block rounded-lg border border-gray-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="font-semibold text-gray-900 truncate">{campaign.name}</h3>
        <CampaignStatusBadge status={campaign.status} />
      </div>
      <p className="mt-2 text-sm text-gray-600">
        {campaign.budget.currency}{" "}
        {Number(campaign.budget.amount).toLocaleString()}
      </p>
      <p className="mt-1 text-xs text-gray-400">{date}</p>
    </Link>
  );
}
