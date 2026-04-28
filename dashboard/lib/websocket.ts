"use client";

import { useEffect, useMemo, useState } from "react";
import { LiveEvent } from "../types";

const WS = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

export function useGraveyardSocket(apiKeyHash: string) {
  const [events, setEvents] = useState<LiveEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<LiveEvent | null>(null);

  useEffect(() => {
    if (!apiKeyHash) return;
    let attempt = 0;
    let socket: WebSocket | null = null;
    let timer: ReturnType<typeof setTimeout> | null = null;

    const connect = () => {
      socket = new WebSocket(`${WS}/ws/${apiKeyHash}`);
      socket.onopen = () => {
        attempt = 0;
        setIsConnected(true);
      };
      socket.onclose = () => {
        setIsConnected(false);
        const delay = Math.min(10000, 500 * 2 ** attempt++);
        timer = setTimeout(connect, delay);
      };
      socket.onmessage = (msg) => {
        const event = JSON.parse(msg.data) as LiveEvent;
        setLastEvent(event);
        setEvents((prev) => [event, ...prev].slice(0, 100));
      };
    };
    connect();
    return () => {
      if (timer) clearTimeout(timer);
      socket?.close();
    };
  }, [apiKeyHash]);

  return useMemo(() => ({ events, isConnected, lastEvent }), [events, isConnected, lastEvent]);
}
