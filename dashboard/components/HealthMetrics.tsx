import { AnalyticsOverview } from "../types";

export default function HealthMetrics({
  overview,
  communityPoolCount,
  communityNewToday,
}: {
  overview: AnalyticsOverview | null;
  communityPoolCount?: number;
  communityNewToday?: number;
}) {
  const safeTotalFailures = overview?.total_failures ?? 0;
  const safeWisdomInjections = overview?.wisdom_injections_count ?? 0;
  const safeCommunity = communityPoolCount ?? 0;

  const cards = [
    {
      label: "Total Failures",
      value: safeTotalFailures,
      color: "var(--color-failure)",
      sub: `+${overview?.failures_this_week ?? 0} this week`,
      renderValue: (n: number) => String(n),
    },
    {
      label: "Self-Heal Rate",
      value: overview ? Math.round(overview.self_heal_success_rate * 100) : 0,
      color: "var(--accent)",
      sub: "of failures auto-resolved",
      renderValue: (n: number) => `${n}%`,
    },
    {
      label: "Wisdom Injections",
      value: safeWisdomInjections,
      color: "var(--text-primary)",
      sub: "pre-task briefings fired",
      renderValue: (n: number) => n.toLocaleString(),
    },
    {
      label: "Community Pool",
      value: safeCommunity,
      color: "var(--color-community)",
      sub: communityNewToday !== undefined ? `↑ ${communityNewToday} new today` : "community-shared failures",
      renderValue: (n: number) => n.toLocaleString(),
    },
  ] as const;

  const maxValue = Math.max(...cards.map((c) => (typeof c.value === "number" ? c.value : 0)), 1);
  return (
    <div className="stat-cards-row grid gap-3 md:grid-cols-4">
      {cards.map((card) => (
        <div key={card.label} className="card-surface p-5">
          <div className="text-xs uppercase tracking-widest" style={{ color: "var(--text-secondary)" }}>
            {card.label}
          </div>
          <div className="font-display mt-2 text-4xl font-extrabold" style={{ color: card.color }}>
            {card.renderValue(card.value as number)}
          </div>
          <div className="mt-2 text-xs" style={{ color: "var(--text-secondary)" }}>
            {card.sub}
          </div>
          <div className="mt-3 h-1.5 rounded-full" style={{ background: "var(--bg-card-elevated)" }}>
            <div
              className="progress-fill h-1.5 rounded-full"
              style={{
                background: card.color,
                width: `${Math.max(0, Math.min(100, Math.round(((card.value as number) / maxValue) * 100)))}%`,
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
