import { FailureMemory } from "../types";

interface TombstoneProps {
  failure: FailureMemory;
  onClick: (failure: FailureMemory) => void;
}

export default function Tombstone({ failure, onClick }: TombstoneProps) {
  const statusIcon = failure.self_heal_succeeded ? "✅" : failure.self_heal_attempted ? "🔄" : "💀";
  return (
    <button
      onClick={() => onClick(failure)}
      className={`tombstone-card w-full rounded-2xl border p-4 text-left ${failure.self_heal_attempted && !failure.self_heal_succeeded ? "healing-card" : ""}`}
      style={{
        background: "var(--bg-card)",
        borderColor: "var(--border)",
        borderTop: failure.self_heal_succeeded ? "2px solid var(--accent)" : undefined,
      }}
    >
      <div className="mb-2 inline-block rounded-full px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-widest" style={{ background: "var(--bg-card-elevated)", color: "var(--text-secondary)" }}>
        {failure.failure_category}
      </div>
      <div className="grid place-items-center py-2">
        <div className="text-3xl" style={{ color: "var(--bg-card-elevated)" }}>🪦</div>
        <div className="font-mono text-xs" style={{ color: "var(--text-tertiary)" }}>R.I.P</div>
        <div className="text-sm font-semibold" style={{ color: "var(--text-secondary)" }}>{failure.agent_name}</div>
      </div>
      <p className="mt-2 line-clamp-2 text-sm">{failure.task_description}</p>
      <div className="mt-3 flex items-center justify-between text-xs" style={{ color: "var(--text-secondary)" }}>
        <span className="rounded-full px-2 py-0.5" style={{ background: "var(--bg-card-elevated)" }}>{failure.error_type}</span>
        <span>{failure.times_occurred > 1 ? `× ${failure.times_occurred}` : "-"}</span>
        <span>{statusIcon}</span>
      </div>
    </button>
  );
}
