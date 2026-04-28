import { AnalyticsOverview } from "../types";

export default function HealthMetrics({ overview }: { overview: AnalyticsOverview | null }) {
  const cards = [
    { label: "Total Failures", value: overview?.total_failures ?? 0 },
    { label: "Self-Heal Rate", value: `${Math.round((overview?.self_heal_success_rate ?? 0) * 100)}%` },
    { label: "Wisdom Injections", value: overview?.wisdom_injections_count ?? 0 },
    { label: "Total Successes", value: overview?.total_successes ?? 0 }
  ];
  return (
    <div className="grid gap-3 md:grid-cols-4">
      {cards.map((card) => (
        <div key={card.label} className="rounded-xl border border-border bg-card p-4">
          <div className="text-xs text-slate-400">{card.label}</div>
          <div className="mt-2 text-2xl">{card.value}</div>
        </div>
      ))}
    </div>
  );
}
