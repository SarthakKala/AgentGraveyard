"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bell, RefreshCw, Settings } from "lucide-react";

const tabs = [
  { href: "/", label: "Failures" },
  { href: "/wisdom", label: "Wisdom Feed" },
  { href: "/analytics", label: "Analytics" },
  { href: "/", label: "Community" },
];

export default function Topbar({ apiKeyHash = "demo-key" }: { apiKeyHash?: string }) {
  const pathname = usePathname();
  return (
    <header className="flex h-14 items-center justify-between border-b px-6" style={{ background: "var(--bg-card-deep)", borderColor: "var(--border)" }}>
      <div className="font-display text-xl font-bold">Graveyard</div>
      <nav className="flex items-center gap-1 rounded-full p-1" style={{ background: "var(--bg-card-hover)" }}>
        {tabs.map((tab) => {
          const active = tab.href === "/" ? pathname === "/" : pathname.startsWith(tab.href);
          return (
            <Link
              key={tab.label}
              href={tab.href}
              className="rounded-full px-4 py-1.5 text-sm font-semibold transition-colors"
              style={{
                background: active ? "var(--accent)" : "transparent",
                color: active ? "var(--accent-text)" : "var(--text-secondary)",
              }}
            >
              {tab.label}
            </Link>
          );
        })}
      </nav>
      <div className="flex items-center gap-2 text-sm">
        <button className="rounded-lg p-2" style={{ background: "var(--bg-card-hover)" }}><Bell size={16} /></button>
        <button className="rounded-lg p-2" style={{ background: "var(--bg-card-hover)" }}><RefreshCw size={16} /></button>
        <button className="rounded-lg p-2" style={{ background: "var(--bg-card-hover)" }}><Settings size={16} /></button>
        <span className="font-mono rounded-full px-3 py-1 text-xs" style={{ background: "var(--bg-card-hover)", color: "var(--text-secondary)" }}>
          {apiKeyHash.slice(0, 3)}-••••••••
        </span>
        <span className="flex items-center gap-1 font-mono text-xs" style={{ color: "var(--accent)" }}>
          <span className="pulse-live inline-block h-2 w-2 rounded-full" style={{ background: "var(--accent)" }} />
          LIVE
        </span>
      </div>
    </header>
  );
}
