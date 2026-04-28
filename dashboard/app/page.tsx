"use client";

import { useEffect, useState } from "react";
import AutopsyReport from "../components/AutopsyReport";
import GraveyardGrid from "../components/GraveyardGrid";
import HealthMetrics from "../components/HealthMetrics";
import LiveMonitor from "../components/LiveMonitor";
import { fetchFailures, fetchOverview } from "../lib/api";
import { AnalyticsOverview, FailureMemory } from "../types";

export default function HomePage() {
  const [apiKeyHash, setApiKeyHash] = useState("demo-key");
  const [failures, setFailures] = useState<FailureMemory[]>([]);
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [selected, setSelected] = useState<FailureMemory | null>(null);

  useEffect(() => {
    fetchFailures(apiKeyHash).then(setFailures).catch(() => setFailures([]));
    fetchOverview(apiKeyHash).then(setOverview).catch(() => setOverview(null));
  }, [apiKeyHash]);

  return (
    <main className="mx-auto max-w-7xl space-y-6 p-6">
      <header className="flex items-center justify-between">
        <h1 className="text-3xl">Agent Graveyard</h1>
        <input
          value={apiKeyHash}
          onChange={(e) => setApiKeyHash(e.target.value)}
          className="rounded-md border border-border bg-card px-3 py-2 text-sm"
          placeholder="API key hash"
        />
      </header>
      <HealthMetrics overview={overview} />
      <section className="grid gap-4 lg:grid-cols-5">
        <div className="lg:col-span-3">
          <GraveyardGrid apiKeyHash={apiKeyHash} failures={failures} onSelect={setSelected} />
        </div>
        <div className="lg:col-span-2">
          <LiveMonitor apiKeyHash={apiKeyHash} />
        </div>
      </section>
      <AutopsyReport failure={selected} onClose={() => setSelected(null)} />
    </main>
  );
}
