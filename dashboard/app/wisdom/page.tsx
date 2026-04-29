"use client";

import { useEffect, useState } from "react";
import { fetchFailures } from "../../lib/api";
import { FailureMemory } from "../../types";
import WisdomFeed from "../../components/WisdomFeed";

export default function WisdomPage() {
  const [apiKeyHash, setApiKeyHash] = useState("demo-key");
  const [failures, setFailures] = useState<FailureMemory[]>([]);
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
    fetchFailures(apiKeyHash, { page: 1, page_size: 100 })
      .then(setFailures)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load wisdom feed."))
      .finally(() => setLoading(false));
  }, [apiKeyHash]);

  return (
    <main className="mx-auto max-w-5xl space-y-4 p-6">
      <div className="flex items-center justify-between gap-4">
        <h1 className="font-display text-3xl">Wisdom Feed</h1>
        <input
          value={apiKeyHash}
          onChange={(e) => setApiKeyHash(e.target.value)}
          className="rounded-md px-2 py-1 text-xs font-mono outline-none"
          style={{ background: "var(--bg-card-elevated)", border: "1px solid var(--border)", color: "var(--text-secondary)" }}
        />
      </div>

      {loading ? (
        <div className="card-surface p-4 text-sm" style={{ color: "var(--text-secondary)" }}>
          Loading wisdom...
        </div>
      ) : error ? (
        <div className="card-surface p-4 text-sm" style={{ color: "var(--color-failure)" }}>
          {error}
        </div>
      ) : null}

      <WisdomFeed failures={failures} />
    </main>
  );
}
