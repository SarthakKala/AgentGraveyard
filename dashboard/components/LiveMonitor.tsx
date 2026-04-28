"use client";

import { useGraveyardSocket } from "../lib/websocket";

export default function LiveMonitor({ apiKeyHash }: { apiKeyHash: string }) {
  const { events, isConnected } = useGraveyardSocket(apiKeyHash);
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <div className="mb-3 text-sm">{isConnected ? "● LIVE" : "Not connected"}</div>
      <div className="max-h-[400px] space-y-2 overflow-y-auto text-sm">
        {events.map((event, idx) => (
          <div key={`${event.session_id}-${idx}`} className="rounded border border-border p-2">
            <div className="font-medium">{event.event_type}</div>
            <div className="text-slate-400">{event.agent_name}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
