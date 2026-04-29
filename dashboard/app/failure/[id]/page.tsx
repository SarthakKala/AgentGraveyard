"use client";

import { useEffect, useState } from "react";
import AutopsyPanel from "../../../components/AutopsyPanel";
import type { FailureMemory } from "../../../types";
import { fetchFailureById } from "../../../lib/api";

interface PageProps {
  params: { id: string };
}

export default function FailureDetailPage({ params }: PageProps) {
  const [failure, setFailure] = useState<FailureMemory | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchFailureById(params.id)
      .then(setFailure)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load failure details."))
      .finally(() => setLoading(false));
  }, [params.id]);

  return (
    <main className="mx-auto max-w-3xl space-y-4 p-6">
      <div>
        <h1 className="text-2xl">Failure {params.id}</h1>
      </div>

      {loading ? (
        <div className="card-surface p-4 text-sm" style={{ color: "var(--text-secondary)" }}>
          Loading failure details...
        </div>
      ) : error ? (
        <div className="card-surface p-4 text-sm" style={{ color: "var(--color-failure)" }}>
          {error}
        </div>
      ) : null}

      <AutopsyPanel failure={failure} />
    </main>
  );
}
