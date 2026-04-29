import { AnalyticsOverview, FailureMemory, LiveEvent } from "../types";

export const mockFailures: FailureMemory[] = [
  {
    id: "f-427-012",
    task_description: "Scrape product pricing from React-based e-commerce site",
    agent_name: "scraper_agent",
    failure_point: "parser_agent",
    failure_reason: "Website uses dynamic JavaScript rendering. Static HTTP requests return empty DOM.",
    error_type: "EmptyResponseError",
    lesson: "React SPAs require browser automation. Static requests return empty shells.",
    suggested_approach: "Use Playwright with headless Chrome instead of requests/BeautifulSoup.",
    failure_category: "TOOL_FAILURE",
    times_occurred: 3,
    resolved_eventually: false,
    self_heal_attempted: true,
    self_heal_succeeded: false,
    is_community_shared: true,
    similarity_score: 0.94,
    created_at: new Date().toISOString(),
  },
  {
    id: "f-501-103",
    task_description: "Normalize user profile JSON before downstream handoff",
    agent_name: "transform_agent",
    failure_point: "validation_step",
    failure_reason: "Unexpected null values triggered schema mismatch.",
    error_type: "ParseError",
    lesson: "Validate JSON shape before parsing and handle nullable fields.",
    suggested_approach: "Apply schema guards and defaults before transformation.",
    failure_category: "DATA_FAILURE",
    times_occurred: 5,
    resolved_eventually: true,
    self_heal_attempted: true,
    self_heal_succeeded: true,
    is_community_shared: false,
    similarity_score: 0.88,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(),
  },
];

export const mockAnalytics: AnalyticsOverview = {
  total_failures: 247,
  total_successes: 891,
  self_heal_success_rate: 0.73,
  most_common_failure_category: "TOOL_FAILURE",
  most_failing_agent: "scraper_agent",
  failures_this_week: 12,
  wisdom_injections_count: 1024,
};

export const mockLiveEvents: LiveEvent[] = [
  {
    event_type: "AGENT_STARTED",
    session_id: "s-001",
    agent_name: "scraper_agent",
    task_description: "Scrape pricing data...",
    timestamp: new Date().toISOString(),
    payload: {},
  },
  {
    event_type: "CORONER_COMPLETE",
    session_id: "s-001",
    agent_name: "coroner_agent",
    task_description: "Autopsy complete",
    timestamp: new Date().toISOString(),
    payload: {},
  },
];
