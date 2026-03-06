"use client";

import { useState } from "react";
import { useCreateCampaign } from "@/hooks/useCreateCampaign";
import type {
  CreateCampaignCreativityInput,
  CreativityType,
  MetricType,
  Operator,
  RuleAction,
} from "@/lib/types";
import { Button } from "@/components/ui/Button";
import { ErrorMessage } from "@/components/ui/ErrorMessage";

const CREATIVITY_TYPES: CreativityType[] = ["BANNER", "VIDEO", "COPY"];
const METRICS: MetricType[] = ["ROAS", "CTR", "CPC", "CPM", "CPA"];
const OPERATORS: { value: Operator; label: string }[] = [
  { value: "GT", label: ">" },
  { value: "GTE", label: ">=" },
  { value: "LT", label: "<" },
  { value: "LTE", label: "<=" },
  { value: "EQ", label: "=" },
];
const ACTIONS: { value: RuleAction; label: string }[] = [
  { value: "PAUSE_CAMPAIGN", label: "Pause Campaign" },
  { value: "REDUCE_BUDGET", label: "Reduce Budget 20%" },
  { value: "SEND_ALERT", label: "Send Alert" },
];
const DEVICE_OPTIONS = ["MOBILE", "DESKTOP", "TABLET"];

const inputCls =
  "w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500";
const selectCls =
  "w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white";

function Label({ children }: { children: React.ReactNode }) {
  return <p className="mb-1 block text-sm font-medium text-gray-700">{children}</p>;
}

function emptyCreativity(): CreateCampaignCreativityInput & { _key: number } {
  return { _key: Date.now(), name: "", type: "BANNER", asset_url: "" };
}

export function FullCampaignForm() {
  const { mutate, createAndSimulate, isPending, error } = useCreateCampaign();
  const [simPending, setSimPending] = useState(false);
  const [simError, setSimError] = useState<string | null>(null);

  // Campaign
  const [name, setName] = useState("");
  const [budgetAmount, setBudgetAmount] = useState("");
  const [budgetCurrency, setBudgetCurrency] = useState("USD");

  // Creativities
  const [creativities, setCreativities] = useState([emptyCreativity()]);

  // Audience
  const [audienceName, setAudienceName] = useState("");
  const [ageMin, setAgeMin] = useState("18");
  const [ageMax, setAgeMax] = useState("65");
  const [locations, setLocations] = useState("");
  const [interests, setInterests] = useState("");
  const [deviceTypes, setDeviceTypes] = useState<string[]>([]);

  // Rule
  const [metric, setMetric] = useState<MetricType>("ROAS");
  const [operator, setOperator] = useState<Operator>("GT");
  const [threshold, setThreshold] = useState("");
  const [ruleAction, setRuleAction] = useState<RuleAction>("PAUSE_CAMPAIGN");

  function addCreativity() {
    setCreativities((prev) => [...prev, emptyCreativity()]);
  }

  function removeCreativity(key: number) {
    setCreativities((prev) => prev.filter((c) => c._key !== key));
  }

  function updateCreativity(key: number, field: keyof CreateCampaignCreativityInput, value: string) {
    setCreativities((prev) =>
      prev.map((c) => (c._key === key ? { ...c, [field]: value } : c)),
    );
  }

  function toggleDevice(device: string) {
    setDeviceTypes((prev) =>
      prev.includes(device) ? prev.filter((d) => d !== device) : [...prev, device],
    );
  }

  function splitList(val: string): string[] {
    return val.split(",").map((s) => s.trim()).filter(Boolean);
  }

  function buildBody() {
    return {
      name,
      budget_amount: Number(budgetAmount),
      budget_currency: budgetCurrency.toUpperCase(),
      creativities: creativities.map(({ name: n, type, asset_url }) => ({ name: n, type, asset_url })),
      audience: {
        name: audienceName,
        age_min: Number(ageMin),
        age_max: Number(ageMax),
        locations: splitList(locations),
        interests: splitList(interests),
        device_types: deviceTypes,
      },
      rule: { metric, operator, threshold: Number(threshold), action: ruleAction },
    };
  }

  function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    mutate(buildBody());
  }

  async function handleCreateAndSimulate(e: React.FormEvent) {
    e.preventDefault();
    setSimPending(true);
    setSimError(null);
    try {
      await createAndSimulate(buildBody());
    } catch (err) {
      setSimError(err instanceof Error ? err.message : "Failed");
    } finally {
      setSimPending(false);
    }
  }

  const busy = isPending || simPending;

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      {/* Campaign */}
      <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
        <h2 className="text-lg font-semibold text-gray-900">Campaign</h2>
        <div>
          <Label>Name</Label>
          <input className={inputCls} value={name} onChange={(e) => setName(e.target.value)} placeholder="Summer Sale 2025" required />
        </div>
        <div className="flex gap-3">
          <div className="flex-1">
            <Label>Budget</Label>
            <input className={inputCls} type="number" min="0.01" step="0.01" value={budgetAmount} onChange={(e) => setBudgetAmount(e.target.value)} placeholder="10000" required />
          </div>
          <div className="w-28">
            <Label>Currency</Label>
            <input className={inputCls} value={budgetCurrency} onChange={(e) => setBudgetCurrency(e.target.value)} maxLength={3} placeholder="USD" />
          </div>
        </div>
      </section>

      {/* Creativities */}
      <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Creativities</h2>
          <button type="button" onClick={addCreativity} className="text-sm font-medium text-indigo-600 hover:text-indigo-800">
            + Add Creative
          </button>
        </div>
        {creativities.map((c, i) => (
          <div key={c._key} className="border border-gray-100 rounded-lg p-4 space-y-3 bg-gray-50">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Creative #{i + 1}</span>
              {creativities.length > 1 && (
                <button type="button" onClick={() => removeCreativity(c._key)} className="text-xs text-red-500 hover:text-red-700">
                  Remove
                </button>
              )}
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className="col-span-2">
                <Label>Name</Label>
                <input className={inputCls} value={c.name} onChange={(e) => updateCreativity(c._key, "name", e.target.value)} placeholder="Hero Banner" required />
              </div>
              <div>
                <Label>Type</Label>
                <select className={selectCls} value={c.type} onChange={(e) => updateCreativity(c._key, "type", e.target.value)}>
                  {CREATIVITY_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
            </div>
            <div>
              <Label>Asset URL</Label>
              <input className={inputCls} value={c.asset_url} onChange={(e) => updateCreativity(c._key, "asset_url", e.target.value)} placeholder="https://cdn.example.com/banner.png" required />
            </div>
          </div>
        ))}
      </section>

      {/* Audience */}
      <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
        <h2 className="text-lg font-semibold text-gray-900">Audience</h2>
        <div>
          <Label>Segment Name</Label>
          <input className={inputCls} value={audienceName} onChange={(e) => setAudienceName(e.target.value)} placeholder="US Young Adults" required />
        </div>
        <div className="flex gap-3">
          <div className="flex-1">
            <Label>Min Age</Label>
            <input className={inputCls} type="number" min="0" max="120" value={ageMin} onChange={(e) => setAgeMin(e.target.value)} />
          </div>
          <div className="flex-1">
            <Label>Max Age</Label>
            <input className={inputCls} type="number" min="0" max="120" value={ageMax} onChange={(e) => setAgeMax(e.target.value)} />
          </div>
        </div>
        <div>
          <Label>Locations <span className="text-gray-400 font-normal">(comma-separated)</span></Label>
          <input className={inputCls} value={locations} onChange={(e) => setLocations(e.target.value)} placeholder="US, UK, CA" />
        </div>
        <div>
          <Label>Interests <span className="text-gray-400 font-normal">(comma-separated)</span></Label>
          <input className={inputCls} value={interests} onChange={(e) => setInterests(e.target.value)} placeholder="sports, tech, fashion" />
        </div>
        <div>
          <Label>Devices</Label>
          <div className="flex gap-4">
            {DEVICE_OPTIONS.map((d) => (
              <label key={d} className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                <input type="checkbox" checked={deviceTypes.includes(d)} onChange={() => toggleDevice(d)} className="rounded border-gray-300 text-indigo-600" />
                {d}
              </label>
            ))}
          </div>
        </div>
      </section>

      {/* Rule */}
      <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
        <h2 className="text-lg font-semibold text-gray-900">Performance Rule</h2>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <Label>Metric</Label>
            <select className={selectCls} value={metric} onChange={(e) => setMetric(e.target.value as MetricType)}>
              {METRICS.map((m) => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
          <div>
            <Label>Operator</Label>
            <select className={selectCls} value={operator} onChange={(e) => setOperator(e.target.value as Operator)}>
              {OPERATORS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          </div>
        </div>
        <div>
          <Label>Threshold</Label>
          <input className={inputCls} type="number" step="any" value={threshold} onChange={(e) => setThreshold(e.target.value)} placeholder="2.5" required />
        </div>
        <div>
          <Label>Action</Label>
          <select className={selectCls} value={ruleAction} onChange={(e) => setRuleAction(e.target.value as RuleAction)}>
            {ACTIONS.map((a) => <option key={a.value} value={a.value}>{a.label}</option>)}
          </select>
        </div>
      </section>

      {error && <ErrorMessage message={error.message} />}
      {simError && <ErrorMessage message={simError} />}

      <div className="flex gap-3 pb-8">
        <Button type="submit" onClick={handleCreate} disabled={busy} loading={isPending} className="flex-1">
          Create Campaign
        </Button>
        <Button type="button" onClick={handleCreateAndSimulate} disabled={busy} loading={simPending} className="flex-1 bg-indigo-700 hover:bg-indigo-800">
          Create &amp; Simulate
        </Button>
      </div>
    </div>
  );
}
