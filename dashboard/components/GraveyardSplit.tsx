"use client";

import { useMemo, useState } from "react";
import { FailureMemory } from "../types";
import AutopsyPanel from "./AutopsyPanel";
import FailureRow from "./FailureRow";

export default function GraveyardSplit({ failures }: { failures: FailureMemory[] }) {
  const [selectedId, setSelectedId] = useState<string | null>(failures[0]?.id ?? null);
  const [tab, setTab] = useState<"all" | "unresolved" | "healed">("all");

  const filtered = useMemo(() => {
    if (tab === "unresolved") return failures.filter((f) => !f.resolved_eventually);
    if (tab === "healed") return failures.filter((f) => f.self_heal_succeeded);
    return failures;
  }, [failures, tab]);

  const selected = filtered.find((f) => f.id === selectedId) ?? filtered[0] ?? null;

  return (
    <section className="split-panel flex gap-4">
      <div className="card-surface w-full overflow-hidden lg:w-[45%]">
        <div className="flex items-center gap-2 border-b p-3" style={{ borderColor: "var(--border)" }}>
          <Tab label="All Failures" active={tab === "all"} onClick={() => setTab("all")} />
          <Tab label="Unresolved" active={tab === "unresolved"} onClick={() => setTab("unresolved")} />
          <Tab label="Self-Healed" active={tab === "healed"} onClick={() => setTab("healed")} />
        </div>
        <div className="max-h-[560px] overflow-y-auto">
          {filtered.map((failure) => (
            <FailureRow
              key={failure.id}
              failure={failure}
              selected={selected?.id === failure.id}
              onSelect={(f) => setSelectedId(f.id)}
            />
          ))}
        </div>
      </div>
      <div className="detail-panel hidden flex-1 lg:block">
        <AutopsyPanel failure={selected} />
      </div>
    </section>
  );
}

function Tab({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="rounded-full px-3 py-1 text-sm font-semibold"
      style={{
        background: active ? "var(--accent)" : "transparent",
        color: active ? "var(--accent-text)" : "var(--text-secondary)",
      }}
    >
      {label}
    </button>
  );
}
