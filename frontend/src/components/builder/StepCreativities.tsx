"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ErrorMessage } from "@/components/ui/ErrorMessage";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { useAddCreativity } from "@/hooks/useAddCreativity";
import type { Campaign, CreativityType } from "@/lib/types";

const TYPE_OPTIONS = [
  { value: "BANNER", label: "Banner" },
  { value: "VIDEO", label: "Video" },
  { value: "COPY", label: "Copy" },
];

const TYPE_ICONS: Record<CreativityType, string> = {
  BANNER: "🖼️",
  VIDEO: "🎬",
  COPY: "📝",
};

export function StepCreativities({ campaign }: { campaign: Campaign }) {
  const { mutateAsync, isPending, error } = useAddCreativity(campaign.id);

  const [name, setName] = useState("");
  const [type, setType] = useState<CreativityType>("BANNER");
  const [assetUrl, setAssetUrl] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await mutateAsync({ name: name.trim(), type, asset_url: assetUrl.trim() });
    setName("");
    setAssetUrl("");
  }

  return (
    <div className="flex flex-col gap-6">
       {!campaign.id && (
      <Card>
        <h2 className="mb-4 text-base font-semibold text-gray-900">
          Add Creativity
        </h2>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            label="Name"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <Select
            label="Type"
            options={TYPE_OPTIONS}
            value={type}
            onChange={(e) => setType(e.target.value as CreativityType)}
          />
          <Input
            label="Asset URL"
            required
            type="url"
            value={assetUrl}
            onChange={(e) => setAssetUrl(e.target.value)}
          />
          {error && <ErrorMessage message={error.message} />}
          <div className="flex justify-end">
            <Button type="submit" loading={isPending}>
              Add Creativity
            </Button>
          </div>
        </form>
      </Card>
       )}
      {campaign.creativities.length > 0 && (
        <Card>
          <h2 className="mb-3 text-base font-semibold text-gray-900">
            Creativities ({campaign.creativities.length})
          </h2>
          <ul className="divide-y divide-gray-100">
            {campaign.creativities.map((c) => (
              <li key={c.id} className="flex items-center gap-3 py-3">
                <span className="text-xl">{TYPE_ICONS[c.type]}</span>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-900">{c.name}</p>
                  <p className="truncate text-xs text-gray-400">{c.asset_url}</p>
                </div>
                <span className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
                  {c.type}
                </span>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}
