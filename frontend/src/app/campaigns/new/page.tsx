import Link from "next/link";
import { FullCampaignForm } from "@/components/campaigns/FullCampaignForm";

export default function NewCampaignPage() {
  return (
    <main className="min-h-screen bg-gray-50 py-10 px-4">
      <div className="max-w-2xl mx-auto mb-6">
        <Link href="/" className="text-sm text-indigo-600 hover:underline">
          ← All Campaigns
        </Link>
        <h1 className="mt-2 text-2xl font-bold text-gray-900">New Campaign</h1>
        <p className="text-sm text-gray-500 mt-1">
          Fill in all sections, then create or immediately simulate.
        </p>
      </div>
      <FullCampaignForm />
    </main>
  );
}
