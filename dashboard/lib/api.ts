import { AnalyticsOverview, FailureMemory } from "../types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchFailures(apiKeyHash: string): Promise<FailureMemory[]> {
  const res = await fetch(`${API}/api/failures?api_key_hash=${apiKeyHash}`, { cache: "no-store" });
  const data = await res.json();
  return data.items || [];
}

export async function fetchOverview(apiKeyHash: string): Promise<AnalyticsOverview> {
  const res = await fetch(`${API}/api/analytics/overview?api_key_hash=${apiKeyHash}`, { cache: "no-store" });
  return res.json();
}
