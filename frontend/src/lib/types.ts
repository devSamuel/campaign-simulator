// ── Enums ──────────────────────────────────────────────────────────────────

export type CampaignStatus = "DRAFT" | "ACTIVE" | "PAUSED" | "SIMULATING";
export type CreativityType = "BANNER" | "VIDEO" | "COPY";
export type MetricType = "ROAS" | "CTR" | "CPC" | "CPM" | "CPA";
export type Operator = "LT" | "GT" | "LTE" | "GTE" | "EQ";
export type RuleAction = "PAUSE_CAMPAIGN" | "REDUCE_BUDGET" | "SEND_ALERT";

// ── Domain objects ─────────────────────────────────────────────────────────

export interface Budget {
  amount: string; // Decimal comes as string from JSON
  currency: string;
}

export interface Creativity {
  id: string;
  name: string;
  type: CreativityType;
  asset_url: string;
}

export interface AudienceSegment {
  id: string;
  name: string;
  age_min: number;
  age_max: number;
  locations: string[];
  interests: string[];
  device_types: string[];
}

export interface PerformanceRule {
  metric: MetricType;
  operator: Operator;
  threshold: number;
  action: RuleAction;
  description: string | null;
}

export interface Campaign {
  id: string;
  name: string;
  status: CampaignStatus;
  budget: Budget;
  creativities: Creativity[];
  audience_segment: AudienceSegment | null;
  rule: PerformanceRule | null;
  created_at: string;
  updated_at: string;
}

export interface CampaignSummary {
  id: string;
  name: string;
  status: CampaignStatus;
  budget: Budget;
  created_at: string;
}

// ── Simulation ─────────────────────────────────────────────────────────────

export interface StepMetrics {
  ROAS: number;
  CTR: number;
  CPC: number;
  CPM: number;
  CPA: number;
}

export interface SimulationStep {
  step: number;
  hour: number;
  metrics: StepMetrics;
  rule_triggered: boolean;
  rule_description: string | null;
}

export interface SimulationResult {
  job_id: string;
  campaign_id: string;
  triggered: boolean;
  triggered_at_step: number | null;
  final_status: string;
  steps: SimulationStep[];
}

export interface RunSimulationResponse {
  job_id: string;
  stream_url: string;
  poll_url: string;
}

// ── SSE event payloads ─────────────────────────────────────────────────────

export interface SSEConnectedPayload {
  job_id: string;
}

export interface SSEStepPayload {
  type: "step";
  step: number;
  hour: number;
  metrics: StepMetrics;
  rule_triggered: boolean;
  rule_description: string | null;
}

export interface SSECompletedPayload {
  type: "completed";
  triggered: boolean;
  triggered_at_step: number | null;
  final_status: string;
  steps: SimulationStep[];
}

export interface SSEErrorPayload {
  type: "error";
  message: string;
}

// ── Request bodies ─────────────────────────────────────────────────────────

export interface CreateCampaignCreativityInput {
  name: string;
  type: CreativityType;
  asset_url: string;
}

export interface CreateCampaignAudienceInput {
  name: string;
  age_min: number;
  age_max: number;
  locations: string[];
  interests: string[];
  device_types: string[];
}

export interface CreateCampaignRuleInput {
  metric: MetricType;
  operator: Operator;
  threshold: number;
  action: RuleAction;
}

export interface CreateCampaignBody {
  name: string;
  budget_amount: number;
  budget_currency: string;
  creativities: CreateCampaignCreativityInput[];
  audience: CreateCampaignAudienceInput;
  rule: CreateCampaignRuleInput;
}

export interface AddCreativityBody {
  name: string;
  type: CreativityType;
  asset_url: string;
}

export interface SetAudienceBody {
  name: string;
  age_min: number;
  age_max: number;
  locations: string[];
  interests: string[];
  device_types: string[];
}

export interface DefineRuleBody {
  metric: MetricType;
  operator: Operator;
  threshold: number;
  action: RuleAction;
}
