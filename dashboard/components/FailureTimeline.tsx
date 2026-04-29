import { FailureMemory } from "../types";

const FIXED_MONTHS = ["Sep", "Oct", "Nov", "Dec", "Jan"];

function monthShort(d: Date) {
  return d.toLocaleString("en-US", { month: "short" });
}

function initialsFromAgent(agentName: string) {
  const trimmed = agentName.trim();
  if (!trimmed) return "??";
  return trimmed.slice(0, 2).toUpperCase();
}

const TAG_BY_CATEGORY: Record<string, string> = {
  TOOL_FAILURE: "#TOOL",
  DATA_FAILURE: "#DATA",
  ENVIRONMENT_FAILURE: "#ENV",
  PROMPT_FAILURE: "#PROMPT",
  REASONING_FAILURE: "#REASON",
};

export default function FailureTimeline({ failures }: { failures: FailureMemory[] }) {
  const monthBuckets = (() => {
    // First, try the fixed blueprint months.
    const fixedCounts = new Map<string, number>(FIXED_MONTHS.map((m) => [m, 0]));
    for (const f of failures) {
      const d = new Date(f.created_at);
      if (Number.isNaN(d.getTime())) continue;
      const label = monthShort(d);
      if (fixedCounts.has(label)) fixedCounts.set(label, (fixedCounts.get(label) ?? 0) + 1);
    }
    const fixedTotal = Array.from(fixedCounts.values()).reduce((a, b) => a + b, 0);
    if (fixedTotal > 0) {
      return {
        labels: FIXED_MONTHS,
        values: FIXED_MONTHS.map((m) => fixedCounts.get(m) ?? 0),
      };
    }

    // Fallback: use the last 5 months present in data.
    const byYearMonth = new Map<string, { key: string; date: Date; label: string; count: number }>();
    for (const f of failures) {
      const d = new Date(f.created_at);
      if (Number.isNaN(d.getTime())) continue;
      const key = `${d.getFullYear()}-${d.getMonth() + 1}`;
      if (!byYearMonth.has(key)) {
        const firstOfMonth = new Date(d.getFullYear(), d.getMonth(), 1);
        byYearMonth.set(key, { key, date: firstOfMonth, label: monthShort(firstOfMonth), count: 0 });
      }
      byYearMonth.get(key)!.count += 1;
    }
    const sorted = Array.from(byYearMonth.values()).sort((a, b) => a.date.getTime() - b.date.getTime());
    const last5 = sorted.slice(Math.max(0, sorted.length - 5));
    if (last5.length === 0) {
      return { labels: FIXED_MONTHS, values: FIXED_MONTHS.map(() => 0) };
    }
    const labels = last5.map((x) => x.label);
    const values = last5.map((x) => x.count);
    return { labels, values };
  })();

  const max = Math.max(...monthBuckets.values, 1);

  const topAgents = (() => {
    const counts = new Map<string, number>();
    for (const f of failures) counts.set(f.agent_name, (counts.get(f.agent_name) ?? 0) + 1);
    return Array.from(counts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([agent_name, count]) => ({ agent_name, count }));
  })();

  const topCategories = (() => {
    const counts = new Map<string, number>();
    for (const f of failures) counts.set(f.failure_category, (counts.get(f.failure_category) ?? 0) + 1);
    return Array.from(counts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([category, count]) => ({ category, count }));
  })();

  return (
    <section className="timeline-section grid gap-4 lg:grid-cols-[2fr_1fr]">
      <div className="card-surface p-5">
        <div className="mb-4 text-xs uppercase tracking-widest" style={{ color: "var(--text-secondary)" }}>
          Monthly Failure Timeline
        </div>
        <div className="space-y-3">
          {monthBuckets.labels.map((month, i) => (
            <div key={month}>
              <div className="font-mono mb-1 text-xs" style={{ color: "var(--text-tertiary)" }}>{month}</div>
              <div className="h-2 rounded-full" style={{ background: "var(--bg-card-elevated)" }}>
                <div
                  className="h-2 rounded-full"
                  style={{
                    width: `${(monthBuckets.values[i] / max) * 100}%`,
                    background: "var(--accent)",
                  }}
                />
              </div>
            </div>
          ))}
        </div>
        <div className="mt-5 flex -space-x-2">
          {topAgents.map((a) => (
            <div
              key={a.agent_name}
              className="grid h-7 w-7 place-items-center rounded-full border text-[10px] font-semibold"
              style={{
                background: "var(--bg-card-elevated)",
                borderColor: "var(--bg-card)",
                color: "var(--text-primary)",
              }}
            >
              {initialsFromAgent(a.agent_name)}
            </div>
          ))}
          <div className="grid h-7 w-7 place-items-center rounded-full text-[10px]" style={{ background: "var(--bg-card-elevated)", color: "var(--text-secondary)" }}>
            +{Math.max(0, failures.length - topAgents.length)}
          </div>
        </div>
      </div>

      <div className="card-surface p-5">
        <div className="mb-4 text-xs uppercase tracking-widest" style={{ color: "var(--text-secondary)" }}>
          Top Failure Type
        </div>
        {[0, 1, 2].map((i) => {
          const entry = topCategories[i];
          const tag = entry ? TAG_BY_CATEGORY[entry.category] ?? `#${entry.category.replace("_FAILURE", "").slice(0, 4)}` : "#—";
          return (
          <div
            key={`${tag}-${i}`}
            className="mb-2 flex items-center justify-between rounded-xl px-3 py-2 text-sm font-semibold"
            style={
              i === 0 && entry && entry.count > 0
                ? { background: "var(--accent)", color: "var(--accent-text)" }
                : { background: "var(--bg-card-elevated)", color: "var(--text-secondary)" }
            }
          >
            <span className="font-mono">{tag}</span>
            <span className="font-mono">{entry ? entry.count : 0}</span>
          </div>
          );
        })}
        <button
          className="btn-accent mt-4 rounded-full px-4 py-2 text-sm font-semibold"
          disabled={failures.length === 0}
          style={failures.length === 0 ? { opacity: 0.5, cursor: "not-allowed" } : undefined}
          // Real self-heal is triggered server-side during SDK event ingestion.
          // This button is intentionally non-destructive/no-op for now.
          onClick={() => undefined}
        >
          Fix now →
        </button>
      </div>
    </section>
  );
}
