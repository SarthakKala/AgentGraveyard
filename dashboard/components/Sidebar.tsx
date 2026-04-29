"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart2, LayoutGrid, Lightbulb, Settings, Skull } from "lucide-react";

const nav = [
  { href: "/", icon: LayoutGrid, label: "Dashboard" },
  { href: "/", icon: Skull, label: "Graveyard" },
  { href: "/analytics", icon: BarChart2, label: "Analytics" },
  { href: "/wisdom", icon: Lightbulb, label: "Wisdom" },
  { href: "/settings", icon: Settings, label: "Settings" },
];

export default function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="sidebar flex h-screen w-16 flex-col items-center justify-between border-r px-2 py-4" style={{ background: "var(--bg-card-deep)", borderColor: "var(--border)" }}>
      <div className="space-y-4">
        <div className="grid h-10 w-10 place-items-center rounded-xl text-xl" style={{ color: "var(--accent)", background: "rgba(196,241,53,0.08)" }}>
          🪦
        </div>
        <nav className="space-y-2">
          {nav.map(({ href, icon: Icon, label }) => {
            const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
            return (
              <Link
                key={`${href}-${label}`}
                href={href}
                title={label}
                className="grid h-10 w-10 place-items-center rounded-xl transition-colors"
                style={{
                  color: active ? "var(--accent)" : "var(--text-tertiary)",
                  background: active ? "rgba(196,241,53,0.12)" : "transparent",
                }}
              >
                <Icon size={18} />
              </Link>
            );
          })}
        </nav>
      </div>
      <div className="relative grid h-10 w-10 place-items-center rounded-full text-xs font-semibold" style={{ background: "var(--bg-card-elevated)" }}>
        AG
        <span className="pulse-live absolute -right-0.5 -top-0.5 h-2.5 w-2.5 rounded-full" style={{ background: "var(--color-success)" }} />
      </div>
    </aside>
  );
}
