export interface FailureMemory {
  id: string;
  task_description: string;
  agent_name: string;
  failure_point: string;
  failure_reason: string;
  error_type: string;
  lesson: string;
  suggested_approach: string;
  failure_category: "TOOL_FAILURE" | "PROMPT_FAILURE" | "DATA_FAILURE" | "ENVIRONMENT_FAILURE" | "REASONING_FAILURE";
  times_occurred: number;
  resolved_eventually: boolean;
  self_heal_attempted: boolean;
  self_heal_succeeded: boolean;
  is_community_shared: boolean;
  created_at: string;
}

export interface AnalyticsOverview {
  total_failures: number;
  total_successes: number;
  self_heal_success_rate: number;
  most_common_failure_category: string;
  most_failing_agent: string;
  failures_this_week: number;
  wisdom_injections_count: number;
}

export interface LiveEvent {
  event_type: string;
  session_id: string;
  agent_name: string;
  task_description: string;
  timestamp: string;
  payload: Record<string, unknown>;
}
