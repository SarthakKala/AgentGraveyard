import { AnalyticsOverview, CategoryCount, FailureMemory } from "../types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function requestJson<T>(input: string): Promise<T> {
  const res = await fetch(input, { cache: "no-store" });
  if (!res.ok) {
    // Try to read a useful message (backend uses `detail` sometimes).
    let detail: string | undefined;
    try {
      const body = (await res.json()) as unknown;
      if (typeof body === "object" && body && "detail" in body && typeof (body as any).detail === "string") {
        detail = (body as any).detail;
      }
    } catch {
      // ignore
    }
    throw new Error(`API request failed (${res.status}): ${detail ?? res.statusText}`);
  }
  return (await res.json()) as T;
}

export async function fetchFailures(
  apiKeyHash: string,
  opts?: {
    failure_category?: string;
    agent_name?: string;
    resolved?: boolean;
    page?: number;
    page_size?: number;
  },
): Promise<FailureMemory[]> {
  const params = new URLSearchParams({ api_key_hash: apiKeyHash });
  if (opts?.failure_category) params.set("failure_category", opts.failure_category);
  if (opts?.agent_name) params.set("agent_name", opts.agent_name);
  if (typeof opts?.resolved === "boolean") params.set("resolved", String(opts.resolved));
  if (opts?.page) params.set("page", String(opts.page));
  if (opts?.page_size) params.set("page_size", String(opts.page_size));

  const data = await requestJson<{ items?: FailureMemory[] }>(`${API}/api/failures?${params.toString()}`);
  return data.items ?? [];
}

export async function fetchFailureById(failureId: string): Promise<FailureMemory> {
  return requestJson<FailureMemory>(`${API}/api/failures/${encodeURIComponent(failureId)}`);
}

export async function updateFailure(
  failureId: string,
  payload: Partial<Pick<FailureMemory, "resolved_eventually" | "lesson" | "suggested_approach" | "is_community_shared"> & Record<string, unknown>>,
): Promise<FailureMemory> {
  const res = await fetch(`${API}/api/failures/${encodeURIComponent(failureId)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    let detail: string | undefined;
    try {
      const body = (await res.json()) as any;
      detail = typeof body?.detail === "string" ? body.detail : undefined;
    } catch {
      // ignore
    }
    throw new Error(`API patch failed (${res.status}): ${detail ?? res.statusText}`);
  }
  return (await res.json()) as FailureMemory;
}

export async function deleteFailure(failureId: string): Promise<{ ok: boolean }> {
  const res = await fetch(`${API}/api/failures/${encodeURIComponent(failureId)}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    throw new Error(`API delete failed (${res.status}): ${res.statusText}`);
  }
  return (await res.json()) as { ok: boolean };
}

export async function fetchCommunityFailures(): Promise<FailureMemory[]> {
  return requestJson<FailureMemory[]>(`${API}/api/failures/community`);
}

export async function fetchOverview(apiKeyHash: string): Promise<AnalyticsOverview> {
  return requestJson<AnalyticsOverview>(`${API}/api/analytics/overview?api_key_hash=${apiKeyHash}`);
}

export async function fetchCategoryBreakdown(apiKeyHash: string): Promise<CategoryCount[]> {
  return requestJson<CategoryCount[]>(`${API}/api/analytics/failure-categories?api_key_hash=${apiKeyHash}`);
}

export async function fetchTimeline(apiKeyHash: string): Promise<Array<{ day: string; failures: number }>> {
  return requestJson<Array<{ day: string; failures: number }>>(`${API}/api/analytics/timeline?api_key_hash=${apiKeyHash}`);
}

export async function fetchAgents(apiKeyHash: string): Promise<Array<{ agent_name: string; failures: number }>> {
  return requestJson<Array<{ agent_name: string; failures: number }>>(`${API}/api/analytics/agents?api_key_hash=${apiKeyHash}`);
}

export async function registerSdkUser(): Promise<{ api_key: string; api_key_hash: string }> {
  return requestJson<{ api_key: string; api_key_hash: string }>(`${API}/api/sdk/register`);
}

export async function fetchWisdom(taskDescription: string, apiKeyHash: string): Promise<any> {
  const params = new URLSearchParams({ task_description: taskDescription, api_key_hash: apiKeyHash });
  return requestJson<any>(`${API}/api/sdk/wisdom?${params.toString()}`);
}
