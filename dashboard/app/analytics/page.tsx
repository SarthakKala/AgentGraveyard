"use client";

import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fetchAgents, fetchCategoryBreakdown, fetchOverview, fetchTimeline } from "../../lib/api";
import { AnalyticsOverview, CategoryCount } from "../../types";

export default function AnalyticsPage() {
  const [apiKeyHash, setApiKeyHash] = useState("demo-key");
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [categories, setCategories] = useState<CategoryCount[]>([]);
  const [timeline, setTimeline] = useState<Array<{ day: string; failures: number }>>([]);
  const [agents, setAgents] = useState<Array<{ agent_name: string; failures: number }>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      const stored = localStorage.getItem("ag_api_key_hash");
      if (stored) setApiKeyHash(stored);
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem("ag_api_key_hash", apiKeyHash);
    } catch {
      // ignore
    }
  }, [apiKeyHash]);

  useEffect(() => {
    if (!apiKeyHash) {
      setError("Missing api_key_hash.");
      return;
    }
    setLoading(true);
    setError(null);
    Promise.all([
      fetchOverview(apiKeyHash),
      fetchCategoryBreakdown(apiKeyHash),
      fetchTimeline(apiKeyHash),
      fetchAgents(apiKeyHash),
    ])
      .then(([ov, cat, tl, ag]) => {
        setOverview(ov);
        setCategories(cat);
        setTimeline(tl);
        setAgents(ag);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load analytics."))
      .finally(() => setLoading(false));
  }, [apiKeyHash]);

  const areaData = timeline
    .slice(-30)
    .map((p) => ({ day: p.day, failures: p.failures }));

  const donut = categories.map((c) => ({ name: c.category, value: c.count }));
  const byAgent = agents.map((a) => ({ agent: a.agent_name, count: a.failures })).sort((a, b) => b.count - a.count);

  const totalFailures = overview?.total_failures ?? 0;
  const succeeded = overview ? Math.round(overview.self_heal_success_rate * totalFailures) : 0;
  const unresolved = Math.max(0, totalFailures - succeeded);

  return (
    <main className="mx-auto max-w-6xl space-y-6 p-6">
      <div className="flex items-center justify-between gap-4">
        <h1 className="font-display text-3xl">Analytics</h1>
        <input
          value={apiKeyHash}
          onChange={(e) => setApiKeyHash(e.target.value)}
          className="rounded-md px-2 py-1 text-xs font-mono outline-none"
          style={{ background: "var(--bg-card-elevated)", border: "1px solid var(--border)", color: "var(--text-secondary)" }}
        />
      </div>

      {loading ? (
        <div className="card-surface p-4 text-sm" style={{ color: "var(--text-secondary)" }}>
          Loading analytics...
        </div>
      ) : error ? (
        <div className="card-surface p-4 text-sm" style={{ color: "var(--color-failure)" }}>
          {error}
        </div>
      ) : null}

      <div className="card-surface h-80 p-4">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={areaData}>
            <defs>
              <linearGradient id="failGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ff4d4d" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#ff4d4d" stopOpacity={0.04} />
              </linearGradient>
            </defs>
            <XAxis dataKey="day" stroke="#8a9a8a" />
            <YAxis stroke="#8a9a8a" />
            <Tooltip />
            <Area type="monotone" dataKey="failures" stroke="#ff4d4d" fill="url(#failGrad)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        <div className="card-surface h-72 p-4">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={donut} dataKey="value" nameKey="name" innerRadius={60} outerRadius={90} />
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="card-surface h-72 p-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={byAgent}>
              <XAxis dataKey="agent" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#c4f135" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="card-surface space-y-2 p-4 md:col-span-2">
          <h3 className="font-display text-xl">Self-Heal Funnel</h3>
          <FunnelBar
            label={`Total Failures: ${totalFailures}`}
            width="100%"
            color="#ff4d4d"
          />
          <FunnelBar
            label={`Self-Heal Succeeded: ${succeeded}`}
            width={`${totalFailures ? Math.round((succeeded / totalFailures) * 100) : 0}%`}
            color="#4ade80"
          />
          <FunnelBar
            label={`Still Unresolved: ${unresolved}`}
            width={`${totalFailures ? Math.round((unresolved / totalFailures) * 100) : 0}%`}
            color="#818cf8"
          />
        </div>
      </div>
    </main>
  );
}

function FunnelBar({ label, width, color }: { label: string; width: string; color: string }) {
  return (
    <div className="h-10 rounded-xl px-4 text-sm font-semibold flex items-center" style={{ width, background: color }}>
      {label}
    </div>
  );
}
