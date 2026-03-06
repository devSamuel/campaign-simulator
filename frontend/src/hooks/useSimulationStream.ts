"use client";

import { useEffect, useState } from "react";
import type { SimulationStep, SSECompletedPayload } from "@/lib/types";

interface UseSimulationStreamResult {
  steps: SimulationStep[];
  completed: boolean;
  summary: SSECompletedPayload | null;
  error: string | null;
  isConnected: boolean;
}

export function useSimulationStream(
  campaignId: string,
  jobId: string,
  options?: { enabled?: boolean },
): UseSimulationStreamResult {
  const [steps, setSteps] = useState<SimulationStep[]>([]);
  const [completed, setCompleted] = useState(false);
  const [summary, setSummary] = useState<SSECompletedPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const enabled = options?.enabled ?? true;

  useEffect(() => {
    if (!enabled || !campaignId || !jobId) return;

    // Reset state for a fresh connection
    setSteps([]);
    setCompleted(false);
    setSummary(null);
    setError(null);
    setIsConnected(false);

    const url = `${process.env.NEXT_PUBLIC_API_URL}/campaigns/${campaignId}/simulate/${jobId}/stream`;
    const es = new EventSource(url);

    es.addEventListener("connected", () => {
      setIsConnected(true);
    });

    es.addEventListener("step", (e: MessageEvent) => {
      try {
        const payload = JSON.parse(e.data as string);
        setSteps((prev) => [
          ...prev,
          {
            step: payload.step,
            hour: payload.hour,
            metrics: payload.metrics,
            rule_triggered: payload.rule_triggered,
            rule_description: payload.rule_description ?? null,
          },
        ]);
      } catch {
        // ignore malformed messages
      }
    });

    es.addEventListener("completed", (e: MessageEvent) => {
      try {
        const payload: SSECompletedPayload = JSON.parse(e.data as string);
        setSummary(payload);
        setCompleted(true);
      } catch {
        setCompleted(true);
      }
      es.close();
    });

    // Named SSE error event (has e.data with payload)
    es.addEventListener("error", (e: MessageEvent | Event) => {
      if ("data" in e && e.data) {
        try {
          const payload = JSON.parse(e.data as string) as { message?: string };
          setError(payload.message ?? "Simulation error");
        } catch {
          setError("Simulation error");
        }
      } else {
        // Network-level error (EventSource connection failure)
        setError("Connection lost");
      }
      es.close();
    });

    return () => {
      es.close();
    };
  }, [campaignId, jobId, enabled]);

  return { steps, completed, summary, error, isConnected };
}
