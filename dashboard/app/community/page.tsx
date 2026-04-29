"use client";

import { useEffect, useState } from "react";
import { fetchCommunityFailures } from "../../lib/api";
import WisdomFeed from "../../components/WisdomFeed";
import type { FailureMemory } from "../../types";

export default function CommunityPage() {
  const [failures, setFailures] = useState<FailureMemory[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchCommunityFailures()
      .then(setFailures)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load community pool."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="mx-auto max-w-5xl space-y-4 p-6">
      <div>
        <h1 className="font-display text-3xl">Community Pool</h1>
        <p style={{ color: "var(--text-secondary)" }}>{failures.length ? `${failures.length} shared memories` : "Loading shared memories..."}</p>
      </div>

      {loading ? (
        <div className="card-surface p-4 text-sm" style={{ color: "var(--text-secondary)" }}>
          Loading community...
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
