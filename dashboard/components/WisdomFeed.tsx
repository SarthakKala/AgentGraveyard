import { FailureMemory } from "../types";

export default function WisdomFeed({ failures }: { failures: FailureMemory[] }) {
  const sorted = [...failures].sort((a, b) => b.times_occurred - a.times_occurred);
  return (
    <div className="space-y-3">
      {sorted.map((f) => (
        <div key={f.id} className="rounded-xl border border-border bg-card p-4">
          <div className="text-sm text-slate-400">{f.failure_category}</div>
          <div className="mt-1">{f.lesson}</div>
          <div className="mt-2 text-xs text-slate-500">Occurred {f.times_occurred} times</div>
        </div>
      ))}
    </div>
  );
}
