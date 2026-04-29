import { FailureMemory } from "../types";

export default function AutopsyPanel({ failure }: { failure: FailureMemory | null }) {
  if (!failure) {
    return <div className="card-surface p-5 text-sm" style={{ color: "var(--text-secondary)" }}>Select a failure to view autopsy details.</div>;
  }
  return (
    <div className="card-surface p-5">
      <div className="mb-3 text-xs uppercase tracking-widest" style={{ color: "var(--text-secondary)" }}>
        Failure details
      </div>
      <div className="mb-4 grid gap-2 md:grid-cols-2">
        <div>
          <div className="font-display text-2xl font-bold"># {failure.id}</div>
          <div className="mt-1 text-sm" style={{ color: "var(--text-secondary)" }}>{failure.agent_name}</div>
        </div>
        <div className="rounded-full px-3 py-1 text-xs font-semibold w-fit" style={{ background: "var(--bg-card-elevated)" }}>
          {failure.failure_category}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <Metric label="Tools Attempted" value={String(failure.times_occurred + 1)} />
        <Metric label="Similarity" value={(failure.similarity_score ?? 0.82).toFixed(2)} />
        <Metric label="Times Occurred" value={String(failure.times_occurred)} />
        <Metric label="Self-Heal" value={failure.self_heal_succeeded ? "✓ Succeeded" : "✗ Failed"} />
      </div>
      <section className="mt-4 rounded-xl p-3" style={{ background: "rgba(196,241,53,0.05)", border: "1px solid rgba(196,241,53,0.1)" }}>
        <div className="mb-1 text-xs uppercase tracking-widest" style={{ color: "var(--text-secondary)" }}>Lesson Learned</div>
        <p className="text-sm">{failure.lesson}</p>
      </section>
      <section className="mt-3 rounded-xl p-3" style={{ background: "var(--bg-card-elevated)" }}>
        <div className="mb-1 text-xs uppercase tracking-widest" style={{ color: "var(--text-secondary)" }}>Synthesized Solution</div>
        <p className="text-sm">{failure.suggested_approach}</p>
      </section>
      <div className="mt-4 flex items-center justify-between">
        <div className="flex gap-2">
          <button className="rounded-lg px-3 py-2 text-xs" style={{ background: "var(--bg-card-elevated)" }}>Resolve</button>
          <button className="rounded-lg px-3 py-2 text-xs" style={{ background: "var(--bg-card-elevated)" }}>Share</button>
          <button className="rounded-lg px-3 py-2 text-xs" style={{ background: "var(--bg-card-elevated)" }}>Delete</button>
        </div>
        <button className="btn-accent rounded-full px-5 py-2.5 text-sm font-semibold">Run Self-Heal</button>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl p-3" style={{ background: "var(--bg-card-elevated)" }}>
      <div className="text-xs uppercase tracking-widest" style={{ color: "var(--text-secondary)" }}>{label}</div>
      <div className="mt-1 font-display text-lg font-bold">{value}</div>
    </div>
  );
}
