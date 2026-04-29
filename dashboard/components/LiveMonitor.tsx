"use client";

import { useGraveyardSocket } from "../lib/websocket";

export default function LiveMonitor({ apiKeyHash }: { apiKeyHash: string }) {
  const { events, isConnected } = useGraveyardSocket(apiKeyHash);
  const feed = events;
  return (
    <div className="card-surface h-full p-4">
      <div className="mb-3 flex items-center justify-between text-sm">
        <span className="font-mono flex items-center gap-2" style={{ color: isConnected ? "var(--accent)" : "var(--text-secondary)" }}>
          <span className={`inline-block h-2.5 w-2.5 rounded-full ${isConnected ? "pulse-live" : ""}`} style={{ background: isConnected ? "var(--accent)" : "var(--text-tertiary)" }} />
          LIVE
        </span>
        <span style={{ color: "var(--text-secondary)" }}>Agent Activity</span>
      </div>
      <div className="max-h-[460px] space-y-2 overflow-y-auto text-sm">
        {feed.length === 0 ? (
          <div style={{ color: "var(--text-tertiary)", fontSize: 12, padding: 12 }}>
            {isConnected ? "No live events yet." : "Websocket not connected."}
          </div>
        ) : (
          feed.map((event, idx) => (
            <div key={`${event.session_id}-${idx}`} className="event-enter rounded-xl p-2" style={{ background: "var(--bg-card-elevated)", border: "1px solid rgba(255,255,255,0.04)" }}>
              <div className="font-mono text-[10px]" style={{ color: "var(--text-tertiary)" }}>{event.event_type}</div>
              <div className="text-xs font-semibold">{event.agent_name}</div>
              <div className="truncate text-xs" style={{ color: "var(--text-secondary)" }}>
                {event.task_description}
              </div>
            </div>
          ))
        )}
      </div>
      <div className="mt-3 text-[10px] font-mono" style={{ color: "var(--text-tertiary)" }}>
        {isConnected ? "Connected to ws://localhost:8000" : "Not connected"}
      </div>
    </div>
  );
}
