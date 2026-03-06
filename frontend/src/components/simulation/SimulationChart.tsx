"use client";

import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { SimulationStep } from "@/lib/types";

interface ChartDatum {
  hour: number;
  ROAS: number;
  CTR: number;
  CPC: number;
  CPM: number;
  CPA: number;
}

const LINES: { key: keyof Omit<ChartDatum, "hour">; color: string }[] = [
  { key: "ROAS", color: "#6366f1" },
  { key: "CTR", color: "#10b981" },
  { key: "CPC", color: "#f59e0b" },
  { key: "CPM", color: "#8b5cf6" },
  { key: "CPA", color: "#ef4444" },
];

function toChartData(steps: SimulationStep[]): ChartDatum[] {
  return steps.map((s) => ({
    hour: s.hour,
    ROAS: s.metrics.ROAS,
    CTR: parseFloat((s.metrics.CTR * 100).toFixed(4)),
    CPC: s.metrics.CPC,
    CPM: s.metrics.CPM,
    CPA: s.metrics.CPA,
  }));
}

const SimulationChartInner = React.memo(
  ({ steps }: { steps: SimulationStep[] }) => {
    const data = toChartData(steps);

    return (
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 4, right: 16, left: 0, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="hour"
            label={{ value: "Hour", position: "insideBottom", offset: -2 }}
            tick={{ fontSize: 11 }}
          />
          <YAxis tick={{ fontSize: 11 }} width={48} />
          <Tooltip
            contentStyle={{ fontSize: 12 }}
            formatter={(value: number, name: string) => [
              name === "CTR" ? `${value.toFixed(2)}%` : value.toFixed(3),
              name,
            ]}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          {LINES.map((l) => (
            <Line
              key={l.key}
              type="monotone"
              dataKey={l.key}
              stroke={l.color}
              dot={false}
              strokeWidth={2}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    );
  },
  (prev, next) => prev.steps.length === next.steps.length,
);

SimulationChartInner.displayName = "SimulationChart";

export { SimulationChartInner as SimulationChart };
