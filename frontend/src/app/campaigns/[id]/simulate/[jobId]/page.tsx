"use client";

import Link from "next/link";
import { use } from "react";
import { SimulationView } from "@/components/simulation/SimulationView";

export default function SimulationPage({
  params,
}: {
  params: Promise<{ id: string; jobId: string }>;
}) {
  const { id, jobId } = use(params);

  return (
    <main className="mx-auto max-w-4xl px-4 py-10">
      <div className="mb-6">
        <Link
          href={`/campaigns/${id}`}
          className="text-sm text-indigo-600 hover:underline"
        >
          ← Back to campaign
        </Link>
        <h1 className="mt-2 text-2xl font-bold text-gray-900">
          Simulation Results
        </h1>
        <p className="mt-1 text-xs text-gray-400 font-mono">Job: {jobId}</p>
      </div>

      <SimulationView campaignId={id} jobId={jobId} />
    </main>
  );
}
