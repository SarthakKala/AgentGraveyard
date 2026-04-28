"use client";

import { FailureMemory } from "../types";

export default function AutopsyReport({ failure, onClose }: { failure: FailureMemory | null; onClose: () => void }) {
  if (!failure) return null;
  return (
    <div className="fixed inset-0 z-50 bg-black/80 p-6">
      <div className="mx-auto max-w-3xl rounded-xl border border-border bg-card p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl">Autopsy Report</h2>
          <button onClick={onClose}>Close</button>
        </div>
        <p className="text-sm text-slate-300">Failure ID: {failure.id}</p>
        <p className="mt-2">{failure.failure_reason}</p>
        <div className="mt-4 rounded-md border border-border p-3 text-sm">
          <div>Lesson: {failure.lesson}</div>
          <div>Suggested: {failure.suggested_approach}</div>
        </div>
      </div>
    </div>
  );
}
