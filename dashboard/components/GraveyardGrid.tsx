"use client";

import { useMemo, useState } from "react";
import { FailureMemory } from "../types";
import Tombstone from "./Tombstone";

interface GraveyardGridProps {
  apiKeyHash: string;
  failures: FailureMemory[];
  onSelect: (failure: FailureMemory) => void;
}

export default function GraveyardGrid({ failures, onSelect }: GraveyardGridProps) {
  const [search, setSearch] = useState("");
  const filtered = useMemo(
    () =>
      failures.filter((f) =>
        `${f.task_description} ${f.error_type}`.toLowerCase().includes(search.toLowerCase())
      ),
    [failures, search]
  );
  return (
    <div className="space-y-3">
      <input
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search failures..."
        className="w-full rounded-md border border-border bg-card px-3 py-2 text-sm"
      />
      {filtered.length === 0 ? (
        <div className="rounded-xl border border-border bg-card p-8 text-center text-slate-400">
          No failures yet. Your agents are behaving... for now.
        </div>
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {filtered.map((failure) => (
            <Tombstone key={failure.id} failure={failure} onClick={onSelect} />
          ))}
        </div>
      )}
    </div>
  );
}
