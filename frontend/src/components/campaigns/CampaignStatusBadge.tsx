import { Badge } from "@/components/ui/Badge";
import type { CampaignStatus } from "@/lib/types";

const statusConfig: Record<
  CampaignStatus,
  { variant: "gray" | "green" | "yellow" | "blue"; label: string }
> = {
  DRAFT: { variant: "gray", label: "Draft" },
  ACTIVE: { variant: "green", label: "Active" },
  PAUSED: { variant: "yellow", label: "Paused" },
  SIMULATING: { variant: "blue", label: "Simulating..." },
};

export function CampaignStatusBadge({ status }: { status: CampaignStatus }) {
  const { variant, label } = statusConfig[status] ?? {
    variant: "gray",
    label: status,
  };
  return (
    <Badge variant={variant}>
      {status === "SIMULATING" && (
        <span className="mr-1 inline-block h-2 w-2 animate-pulse rounded-full bg-blue-500" />
      )}
      {label}
    </Badge>
  );
}
