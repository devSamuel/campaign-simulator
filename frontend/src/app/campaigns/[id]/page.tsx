"use client";

import Link from "next/link";
import { use } from "react";
import { CampaignBuilder } from "@/components/builder/CampaignBuilder";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { Spinner } from "@/components/ui/Spinner";
import { useCampaign } from "@/hooks/useCampaign";

export default function CampaignPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data: campaign, isLoading, error } = useCampaign(id);

  return (
    <main className="mx-auto max-w-3xl px-4 py-10">
      <div className="mb-6">
        <Link
          href="/"
          className="text-sm text-indigo-600 hover:underline"
        >
          ← All Campaigns
        </Link>
        {campaign && (
          <h1 className="mt-2 text-2xl font-bold text-gray-900">
            {campaign.name}
          </h1>
        )}
      </div>

      {isLoading && (
        <div className="flex justify-center py-20">
          <Spinner className="h-8 w-8 text-indigo-600" />
        </div>
      )}

      {error && <ErrorMessage message={error.message} />}

      {campaign && <CampaignBuilder campaign={campaign} />}
    </main>
  );
}
