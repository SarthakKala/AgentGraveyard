import { FailureMemory } from "../types";

export default function FailureRow({
  failure,
  selected,
  onSelect,
}: {
  failure: FailureMemory;
  selected: boolean;
  onSelect: (f: FailureMemory) => void;
}) {
  const status = failure.self_heal_succeeded ? "Self-Healed" : failure.self_heal_attempted ? "Healing..." : "Unresolved";
  const badgeStyle =
    status === "Self-Healed"
      ? { background: "rgba(196,241,53,0.15)", color: "var(--accent)" }
      : status === "Healing..."
        ? { background: "rgba(129,140,248,0.15)", color: "var(--color-healing)" }
        : { background: "rgba(255,77,77,0.15)", color: "var(--color-failure)" };

  return (
    <button
      onClick={() => onSelect(failure)}
      className="failure-row flex w-full items-center gap-3 border-b px-4 py-3 text-left"
      style={{
        borderColor: "rgba(255,255,255,0.04)",
        background: selected ? "var(--bg-card-elevated)" : "transparent",
        borderLeft: selected ? "2px solid var(--accent)" : "2px solid transparent",
      }}
    >
      <div className="grid h-8 w-8 place-items-center rounded-full text-xs font-semibold" style={{ background: "var(--bg-card-elevated)" }}>
        {failure.agent_name.slice(0, 2).toUpperCase()}
      </div>
      <div className="min-w-0 flex-1">
        <div className="mb-1 flex items-center gap-2">
          <span className="font-mono text-xs" style={{ color: "var(--text-secondary)" }}>
            #{failure.id}
          </span>
          <span className="rounded-full px-2 py-0.5 text-xs" style={badgeStyle}>
            {status}
          </span>
        </div>
        <p className="truncate text-sm">{failure.task_description}</p>
      </div>
      <div className="font-mono text-xs" style={{ color: "var(--text-secondary)" }}>
        {(failure.similarity_score ?? 0.8).toFixed(2)} sim
      </div>
    </button>
  );
}
