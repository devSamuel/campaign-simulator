import type {
  AddCreativityBody,
  Campaign,
  CampaignSummary,
  CreateCampaignBody,
  Creativity,
  DefineRuleBody,
  RunSimulationResponse,
  SetAudienceBody,
  SimulationResult,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL;

if (!BASE && typeof window !== "undefined") {
  console.error("NEXT_PUBLIC_API_URL is not set");
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((err as { detail?: string }).detail ?? "Unknown error");
  }
  return res.json() as Promise<T>;
}

export async function listCampaigns(params?: {
  limit?: number;
  offset?: number;
}): Promise<CampaignSummary[]> {
  const qs = new URLSearchParams();
  if (params?.limit !== undefined) qs.set("limit", String(params.limit));
  if (params?.offset !== undefined) qs.set("offset", String(params.offset));
  const query = qs.toString() ? `?${qs}` : "";
  return apiFetch<CampaignSummary[]>(`/campaigns${query}`);
}

export async function getCampaign(id: string): Promise<Campaign> {
  return apiFetch<Campaign>(`/campaigns/${id}`);
}

export async function createCampaign(body: CreateCampaignBody): Promise<Campaign> {
  return apiFetch<Campaign>("/campaigns", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function addCreativity(
  campaignId: string,
  body: AddCreativityBody,
): Promise<Creativity> {
  return apiFetch<Creativity>(`/campaigns/${campaignId}/creativities`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function setAudience(
  campaignId: string,
  body: SetAudienceBody,
): Promise<Campaign> {
  return apiFetch<Campaign>(`/campaigns/${campaignId}/audience-segment`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function defineRule(
  campaignId: string,
  body: DefineRuleBody,
): Promise<Campaign> {
  return apiFetch<Campaign>(`/campaigns/${campaignId}/rule`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function runSimulation(
  campaignId: string,
): Promise<RunSimulationResponse> {
  return apiFetch<RunSimulationResponse>(`/campaigns/${campaignId}/simulate`, {
    method: "POST",
  });
}

export async function getSimulationResult(
  campaignId: string,
  jobId: string,
): Promise<SimulationResult | null> {
  try {
    return await apiFetch<SimulationResult>(
      `/campaigns/${campaignId}/simulate/${jobId}`,
    );
  } catch (err) {
    // 404 means still running or not yet cached — return null (not an error)
    if (err instanceof Error && err.message.includes("not found")) return null;
    throw err;
  }
}
