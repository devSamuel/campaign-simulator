"use client";

import Link from "next/link";
import { CampaignCard } from "@/components/campaigns/CampaignCard";
import { Button } from "@/components/ui/Button";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { Spinner } from "@/components/ui/Spinner";
import { useCampaigns } from "@/hooks/useCampaigns";

export default function HomePage() {
  const { data: campaigns, isLoading, error, refetch } = useCampaigns();

  return (
    <main className="mx-auto max-w-5xl px-4 py-10">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campaigns</h1>
          <p className="mt-1 text-sm text-gray-500">
            Create and manage your marketing campaigns
          </p>
        </div>
        <Link href="/campaigns/new">
          <Button>+ New Campaign</Button>
        </Link>
      </div>

      {isLoading && (
        <div className="flex justify-center py-20">
          <Spinner className="h-8 w-8 text-indigo-600" />
        </div>
      )}

      {error && (
        <div className="flex flex-col items-center gap-3 py-10">
          <ErrorMessage message={error.message} />
          <Button variant="secondary" onClick={() => refetch()}>
            Retry
          </Button>
        </div>
      )}

      {!isLoading && !error && campaigns?.length === 0 && (
        <div className="flex flex-col items-center gap-3 py-20 text-gray-400">
          <p className="text-lg">No campaigns yet</p>
          <Link href="/campaigns/new">
            <Button>Create your first campaign</Button>
          </Link>
        </div>
      )}

      {campaigns && campaigns.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {campaigns.map((c) => (
            <CampaignCard key={c.id} campaign={c} />
          ))}
        </div>
      )}
    </main>
  );
}
