"use client";

import { Search } from "lucide-react";

interface Props {
  search: string;
  onSearchChange: (value: string) => void;
  category: string;
  onCategoryChange: (value: string) => void;
}

export default function FilterBar({ search, onSearchChange, category, onCategoryChange }: Props) {
  const activeCount = (category === "ALL" ? 0 : 1) + (search.trim().length > 0 ? 1 : 0);
  return (
    <div className="card-surface flex flex-wrap items-center gap-3 p-3">
      <span className="rounded-full px-3 py-1 text-xs font-semibold" style={{ background: "var(--accent)", color: "var(--accent-text)" }}>
        Active filters: {activeCount}
      </span>
      <select
        className="rounded-[10px] px-3 py-2 text-sm outline-none"
        style={{ background: "var(--bg-card-elevated)", border: "1px solid var(--border)", color: "var(--text-secondary)" }}
        value={category}
        onChange={(e) => onCategoryChange(e.target.value)}
      >
        <option value="ALL">All Categories</option>
        <option value="TOOL_FAILURE">TOOL_FAILURE</option>
        <option value="PROMPT_FAILURE">PROMPT_FAILURE</option>
        <option value="DATA_FAILURE">DATA_FAILURE</option>
        <option value="ENVIRONMENT_FAILURE">ENVIRONMENT_FAILURE</option>
        <option value="REASONING_FAILURE">REASONING_FAILURE</option>
      </select>
      <div className="ml-auto flex items-center gap-2 rounded-[10px] px-3 py-2" style={{ background: "var(--bg-card-elevated)", border: "1px solid var(--border)" }}>
        <Search size={14} style={{ color: "var(--text-tertiary)" }} />
        <input
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search failures..."
          className="bg-transparent text-sm outline-none"
          style={{ color: "var(--text-primary)" }}
        />
      </div>
    </div>
  );
}
