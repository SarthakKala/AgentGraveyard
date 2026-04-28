import { FailureMemory } from "../types";

interface TombstoneProps {
  failure: FailureMemory;
  onClick: (failure: FailureMemory) => void;
}

export default function Tombstone({ failure, onClick }: TombstoneProps) {
  return (
    <button onClick={() => onClick(failure)} className="w-full rounded-xl border border-border bg-card p-4 text-left hover:border-accent">
      <div className="text-xs text-slate-400">{failure.failure_category}</div>
      <div className="mt-2 text-lg">RIP {failure.agent_name}</div>
      <p className="mt-2 line-clamp-2 text-sm text-slate-300">{failure.task_description}</p>
      <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
        <span>{failure.error_type}</span>
        <span>{failure.times_occurred > 1 ? `x ${failure.times_occurred}` : "-"}</span>
      </div>
    </button>
  );
}
