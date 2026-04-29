"use client";

import { useEffect, useMemo, useState } from "react";
import type { FailureMemory } from "../types";

type LiveEvent = {
  type: string;
  agent: string;
  desc: string;
  time: string;
  color: string;
  bg: string;
  icon: string;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

const CATEGORY_COLORS: Record<string, { bg: string; text: string }> = {
  TOOL_FAILURE: { bg: "rgba(248,113,113,0.15)", text: "#f87171" },
  DATA_FAILURE: { bg: "rgba(251,191,36,0.15)", text: "#fbbf24" },
  PROMPT_FAILURE: { bg: "rgba(251,146,60,0.15)", text: "#fb923c" },
  ENVIRONMENT_FAILURE: { bg: "rgba(96,165,250,0.15)", text: "#60a5fa" },
  REASONING_FAILURE: { bg: "rgba(192,132,252,0.15)", text: "#c084fc" },
};

const STATUS_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  healing: { bg: "rgba(129,140,248,0.15)", text: "#818cf8", label: "Healing..." },
  healed: { bg: "rgba(196,241,53,0.15)", text: "#c4f135", label: "Self-Healed" },
  unresolved: { bg: "rgba(255,77,77,0.15)", text: "#ff4d4d", label: "Unresolved" },
};

const simColor = (s: number) => (s > 0.9 ? "#ff4d4d" : s > 0.75 ? "#fbbf24" : "#4ade80");

function toUiStatus(f: FailureMemory) {
  if (f.self_heal_attempted && !f.self_heal_succeeded) return "healing";
  if (f.self_heal_succeeded || f.resolved_eventually) return "healed";
  return "unresolved";
}

function toLiveEvent(eventType: string, payload: Record<string, unknown>, agent: string): LiveEvent {
  const map: Record<string, { color: string; bg: string; icon: string }> = {
    AGENT_STARTED: { color: "#c4f135", bg: "rgba(196,241,53,0.15)", icon: "⚡" },
    WISDOM_INJECTED: { color: "#fbbf24", bg: "rgba(251,191,36,0.15)", icon: "💡" },
    AGENT_SUCCEEDED: { color: "#4ade80", bg: "rgba(74,222,128,0.15)", icon: "✓" },
    AGENT_FAILED: { color: "#ff4d4d", bg: "rgba(255,77,77,0.15)", icon: "✗" },
    CORONER_STARTED: { color: "#818cf8", bg: "rgba(129,140,248,0.15)", icon: "🧠" },
    CORONER_COMPLETE: { color: "#818cf8", bg: "rgba(129,140,248,0.15)", icon: "📋" },
    SELF_HEAL_STARTED: { color: "#60a5fa", bg: "rgba(96,165,250,0.15)", icon: "🔄" },
    SELF_HEAL_SUCCEEDED: { color: "#4ade80", bg: "rgba(74,222,128,0.15)", icon: "💚" },
    SELF_HEAL_FAILED: { color: "#ff4d4d", bg: "rgba(255,77,77,0.15)", icon: "💀" },
  };
  const info = map[eventType] || map.AGENT_STARTED;
  return {
    type: eventType,
    agent: agent || "agent",
    desc: String(payload?.description || payload?.task_description || "Live event received"),
    time: "just now",
    color: info.color,
    bg: info.bg,
    icon: info.icon,
  };
}

const Badge = ({ status }: { status: string }) => {
  const s = STATUS_STYLES[status] || STATUS_STYLES.unresolved;
  return (
    <span style={{ background: s.bg, color: s.text, borderRadius: 999, padding: "2px 7px", fontSize: 9, fontWeight: 700, fontFamily: "'DM Mono', monospace" }}>
      {s.label}
    </span>
  );
};

const CatBadge = ({ cat }: { cat: string }) => {
  const c = CATEGORY_COLORS[cat] || { bg: "rgba(138,154,138,0.15)", text: "#8a9a8a" };
  return <span style={{ background: c.bg, color: c.text, borderRadius: 999, padding: "3px 10px", fontSize: 10, fontWeight: 600 }}>{cat}</span>;
};

const Avatar = ({ initials, color, size = 28 }: { initials: string; color: string; size?: number }) => (
  <div style={{ width: size, height: size, borderRadius: "50%", background: color, display: "flex", alignItems: "center", justifyContent: "center", fontSize: size * 0.3, fontWeight: 700, color: "#fff", flexShrink: 0 }}>
    {initials}
  </div>
);

export default function AgentGraveyardDashboard() {
  const [apiKey, setApiKey] = useState("demo-key");
  const [failures, setFailures] = useState<FailureMemory[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("Failures");
  const [listTab, setListTab] = useState("All Failures");
  const [events, setEvents] = useState<LiveEvent[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(`${API_URL}/api/failures?api_key_hash=${apiKey}`, { cache: "no-store" });
        const data = await res.json();
        const rows = (data.items || []) as FailureMemory[];
        setFailures(rows);
        if (rows.length && !selectedId) setSelectedId(rows[0].id);
      } catch {
        setFailures([]);
      }
    };
    load();
  }, [apiKey, selectedId]);

  useEffect(() => {
    if (!apiKey) return;
    const ws = new WebSocket(`${WS_URL}/ws/${apiKey}`);
    ws.onmessage = (msg) => {
      try {
        const raw = JSON.parse(msg.data) as Record<string, unknown>;
        const ev = toLiveEvent(
          String(raw.event_type || "AGENT_STARTED"),
          (raw.payload as Record<string, unknown>) || {},
          String(raw.agent_name || ""),
        );
        setEvents((prev) => [ev, ...prev].slice(0, 10));
      } catch {
        // no-op
      }
    };
    return () => ws.close();
  }, [apiKey]);

  const tabs = ["Failures", "Wisdom Feed", "Analytics", "Community"];
  const listTabs = ["All Failures", "Unresolved", "Self-Healed"];

  const filteredFailures = useMemo(() => {
    if (listTab === "Unresolved") return failures.filter((f) => toUiStatus(f) === "unresolved");
    if (listTab === "Self-Healed") return failures.filter((f) => toUiStatus(f) === "healed");
    return failures;
  }, [failures, listTab]);

  const selected = filteredFailures.find((f) => f.id === selectedId) || filteredFailures[0] || null;

  return (
    <div style={{ background: "#0a0c0a", minHeight: "100vh", color: "#f0f4f0", fontFamily: "'DM Sans', sans-serif" }}>
      <div style={{ background: "#0e110e", borderBottom: "1px solid rgba(255,255,255,0.06)", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 20px", position: "sticky", top: 0, zIndex: 50 }}>
        <div style={{ fontFamily: "'Syne', sans-serif", fontSize: 16, fontWeight: 800, color: "#c4f135" }}>🪦 AG</div>
        <div style={{ display: "flex", background: "#161916", borderRadius: 999, padding: 3, gap: 2 }}>
          {tabs.map((t) => (
            <button key={t} onClick={() => setActiveTab(t)} style={{ padding: "5px 14px", borderRadius: 999, fontSize: 12, cursor: "pointer", border: "none", background: activeTab === t ? "#c4f135" : "transparent", color: activeTab === t ? "#0a0c0a" : "#8a9a8a", fontWeight: activeTab === t ? 700 : 400 }}>
              {t}
            </button>
          ))}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <input value={apiKey} onChange={(e) => setApiKey(e.target.value)} style={{ background: "#1c201c", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 8, padding: "4px 8px", color: "#8a9a8a", fontSize: 11, width: 130 }} />
          <div style={{ width: 7, height: 7, borderRadius: "50%", background: "#c4f135", animation: "pulse 1.5s infinite" }} />
        </div>
      </div>

      <div style={{ padding: "16px 20px", display: "grid", gridTemplateColumns: "1fr 1.5fr", gap: 10 }}>
        <div style={{ background: "#111411", borderRadius: 14, overflow: "hidden", border: "1px solid rgba(255,255,255,0.05)" }}>
          <div style={{ display: "flex", gap: 4, padding: 10, borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
            {listTabs.map((t) => (
              <button key={t} onClick={() => setListTab(t)} style={{ padding: "4px 10px", borderRadius: 999, fontSize: 10, cursor: "pointer", border: "none", background: listTab === t ? "#c4f135" : "transparent", color: listTab === t ? "#0a0c0a" : "#8a9a8a", fontWeight: listTab === t ? 700 : 400 }}>
                {t}
              </button>
            ))}
          </div>
          {filteredFailures.map((f) => {
            const status = toUiStatus(f);
            const similarity = f.similarity_score ?? 0.8;
            const initials = f.agent_name.slice(0, 2).toUpperCase();
            return (
              <div key={f.id} onClick={() => setSelectedId(f.id)} style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 12px", borderBottom: "1px solid rgba(255,255,255,0.04)", cursor: "pointer", background: selected?.id === f.id ? "#1c201c" : "transparent", borderLeft: selected?.id === f.id ? "2px solid #c4f135" : "2px solid transparent" }}>
                <Avatar initials={initials} color="#534AB7" size={30} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 9, color: "#8a9a8a", fontFamily: "'DM Mono', monospace", display: "flex", alignItems: "center", gap: 5, marginBottom: 2 }}>
                    #{f.id} <Badge status={status} />
                  </div>
                  <div style={{ fontSize: 11, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{f.task_description}</div>
                </div>
                <div style={{ fontSize: 10, fontFamily: "'DM Mono', monospace", fontWeight: 700, color: simColor(similarity) }}>{similarity.toFixed(2)} sim</div>
              </div>
            );
          })}
        </div>

        {selected && (
          <div style={{ background: "#111411", borderRadius: 14, padding: 14, border: "1px solid rgba(255,255,255,0.05)", display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ display: "grid", gridTemplateColumns: "auto 1fr auto", alignItems: "center", gap: 12 }}>
              <div style={{ fontFamily: "'Syne', sans-serif", fontSize: 18, fontWeight: 800, display: "flex", alignItems: "center", gap: 6 }}>
                # {selected.id} <Badge status={toUiStatus(selected)} />
              </div>
              <div style={{ fontSize: 13, fontWeight: 600 }}>{selected.agent_name}</div>
              <CatBadge cat={selected.failure_category} />
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
              <Metric label="Tools Attempted" value={String(selected.times_occurred + 1)} />
              <Metric label="Similarity Score" value={(selected.similarity_score ?? 0.8).toFixed(2)} />
              <Metric label="Times Occurred" value={String(selected.times_occurred)} />
              <Metric label="Self-Heal" value={selected.self_heal_succeeded ? "✓ Succeeded" : "✗ Failed"} />
            </div>
            <div style={{ background: "rgba(196,241,53,0.05)", border: "1px solid rgba(196,241,53,0.1)", borderRadius: 10, padding: 12, fontSize: 12 }}>
              {selected.lesson}
            </div>
            <div style={{ background: "#1c201c", borderRadius: 10, padding: 12, fontSize: 12, color: "#8a9a8a" }}>
              {selected.suggested_approach}
            </div>
          </div>
        )}
      </div>

      <div style={{ margin: "0 20px 20px", background: "#0e110e", borderRadius: 14, padding: 14, border: "1px solid rgba(255,255,255,0.05)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 5, color: "#c4f135", fontFamily: "'DM Mono', monospace", fontSize: 12, fontWeight: 700 }}>
            <div style={{ width: 7, height: 7, borderRadius: "50%", background: "#c4f135", animation: "pulse 1.5s infinite" }} />
            LIVE
          </div>
          <span style={{ color: "#8a9a8a", fontSize: 12 }}>Agent Activity</span>
        </div>
        {events.slice(0, 5).map((ev, i) => (
          <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 10, padding: "8px 6px", borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
            <div style={{ width: 22, height: 22, borderRadius: "50%", background: ev.bg, color: ev.color, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10 }}>{ev.icon}</div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 9, color: "#4a5a4a", fontFamily: "'DM Mono', monospace", textTransform: "uppercase" }}>{ev.type}</div>
              <div style={{ fontSize: 11, fontWeight: 600 }}>{ev.agent}</div>
              <div style={{ fontSize: 10, color: "#8a9a8a" }}>{ev.desc}</div>
            </div>
            <div style={{ fontSize: 9, color: "#4a5a4a", fontFamily: "'DM Mono', monospace" }}>{ev.time}</div>
          </div>
        ))}
      </div>

      <style>{`@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }`}</style>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ background: "#1c201c", borderRadius: 10, padding: 10 }}>
      <div style={{ fontSize: 9, color: "#8a9a8a", marginBottom: 3 }}>{label}</div>
      <div style={{ fontFamily: "'Syne', sans-serif", fontSize: 16, fontWeight: 800 }}>{value}</div>
    </div>
  );
}
