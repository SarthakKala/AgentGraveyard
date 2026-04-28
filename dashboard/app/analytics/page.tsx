"use client";

import { useEffect, useState } from "react";
import { Bar, BarChart, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { fetchFailures } from "../../lib/api";
import { FailureMemory } from "../../types";

export default function AnalyticsPage() {
  const [failures, setFailures] = useState<FailureMemory[]>([]);
  useEffect(() => {
    fetchFailures("demo-key").then(setFailures).catch(() => setFailures([]));
  }, []);
  const byCategory = Object.values(
    failures.reduce<Record<string, { name: string; value: number }>>((acc, cur) => {
      acc[cur.failure_category] = acc[cur.failure_category] || { name: cur.failure_category, value: 0 };
      acc[cur.failure_category].value += 1;
      return acc;
    }, {})
  );
  return (
    <main className="mx-auto max-w-6xl space-y-6 p-6">
      <h1 className="text-3xl">Analytics</h1>
      <div className="grid gap-6 md:grid-cols-2">
        <div className="h-72 rounded-xl border border-border bg-card p-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={failures.map((f) => ({ day: f.created_at.slice(0, 10), value: 1 }))}>
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#a855f7" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="h-72 rounded-xl border border-border bg-card p-4">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={byCategory} dataKey="value" nameKey="name" />
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="h-72 rounded-xl border border-border bg-card p-4 md:col-span-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={byCategory}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </main>
  );
}
