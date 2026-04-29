"use client";

import { useEffect, useMemo, useState } from "react";
import FailureTimeline from "../components/FailureTimeline";
import FilterBar from "../components/FilterBar";
import GraveyardSplit from "../components/GraveyardSplit";
import HealthMetrics from "../components/HealthMetrics";
import LiveMonitor from "../components/LiveMonitor";
import { fetchCommunityFailures, fetchFailures, fetchOverview } from "../lib/api";
import type { AnalyticsOverview, FailureMemory } from "../types";

export default function Page() {
  const [apiKeyHash, setApiKeyHash] = useState("demo-key");
  const [failures, setFailures] = useState<FailureMemory[]>([]);
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [communityPoolCount, setCommunityPoolCount] = useState<number | undefined>(undefined);
  const [communityNewToday, setCommunityNewToday] = useState<number | undefined>(undefined);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("ALL");
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
      setFailures([]);
      setOverview(null);
      return;
    }

    setLoading(true);
    setError(null);

    Promise.all([
      fetchFailures(apiKeyHash, { page: 1, page_size: 200 }),
      fetchOverview(apiKeyHash),
    ])
      .then(([items, ov]) => {
        setFailures(items);
        setOverview(ov);
      })
      .catch((e) => {
        setError(e instanceof Error ? e.message : "Failed to load dashboard data.");
        setFailures([]);
        setOverview(null);
      })
      .finally(() => setLoading(false));
  }, [apiKeyHash]);

  useEffect(() => {
    // Community endpoint is not apiKeyHash-scoped; it returns shared memories.
    fetchCommunityFailures()
      .then((items) => {
        setCommunityPoolCount(items.length);
        const now = new Date();
        const todayStr = now.toDateString();
        const newToday = items.filter((x) => {
          const d = new Date(x.created_at);
          if (Number.isNaN(d.getTime())) return false;
          return d.toDateString() === todayStr;
        }).length;
        setCommunityNewToday(newToday);
      })
      .catch(() => {
        setCommunityPoolCount(undefined);
        setCommunityNewToday(undefined);
      });
  }, []);

  const filtered = useMemo(
    () =>
      failures.filter((f) => {
        const bySearch = `${f.task_description} ${f.error_type}`.toLowerCase().includes(search.toLowerCase());
        const byCategory = category === "ALL" || f.failure_category === category;
        return bySearch && byCategory;
      }),
    [failures, search, category],
  );

  return (
    <main className="mx-auto max-w-[1320px] space-y-4 p-4">
      <header className="card-surface flex items-center justify-between rounded-2xl px-4 py-3">
        <div className="flex items-center gap-3">
          <span style={{ fontSize: 14 }}>🪦</span>
          <span className="font-display text-[32px] font-extrabold leading-none" style={{ color: "var(--accent)" }}>
            AG
          </span>
        </div>
        <div className="flex gap-1 rounded-full p-1" style={{ background: "var(--bg-card-hover)" }}>
          {["Failures", "Wisdom Feed", "Analytics", "Community"].map((tab, i) => (
            <span
              key={tab}
              className="rounded-full px-4 py-1.5 text-sm"
              style={{
                background: i === 0 ? "var(--accent)" : "transparent",
                color: i === 0 ? "var(--accent-text)" : "var(--text-secondary)",
                fontWeight: i === 0 ? 700 : 500,
              }}
            >
              {tab}
            </span>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <input
            value={apiKeyHash}
            onChange={(e) => setApiKeyHash(e.target.value)}
            className="rounded-md px-2 py-1 text-xs font-mono outline-none"
            style={{ background: "var(--bg-card-elevated)", border: "1px solid var(--border)", color: "var(--text-secondary)" }}
          />
          <span className="pulse-live inline-block h-2 w-2 rounded-full" style={{ background: "var(--accent)" }} />
          <span className="font-mono text-xs" style={{ color: "var(--text-secondary)" }}>
            LIVE
          </span>
        </div>
      </header>

      <h1 className="font-display text-5xl font-extrabold leading-none">Agent Graveyard</h1>
      {loading ? (
        <div className="card-surface p-4 text-sm" style={{ color: "var(--text-secondary)" }}>
          Loading dashboard data...
        </div>
      ) : error ? (
        <div className="card-surface p-4 text-sm" style={{ color: "var(--color-failure)" }}>
          {error}
        </div>
      ) : null}

      <HealthMetrics
        overview={overview}
        communityPoolCount={communityPoolCount}
        communityNewToday={communityNewToday}
      />
      <FailureTimeline failures={filtered} />
      <FilterBar search={search} onSearchChange={setSearch} category={category} onCategoryChange={setCategory} />

      <section className="grid gap-4 xl:grid-cols-[1fr_320px]">
        <GraveyardSplit failures={filtered} />
        <div className="min-h-[360px]">
          <LiveMonitor apiKeyHash={apiKeyHash} />
        </div>
      </section>
    </main>
  );
}
