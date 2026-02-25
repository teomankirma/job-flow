"use client";

import type { JobStatus } from "@/lib/types";

const TABS: Array<{ value: JobStatus | "all"; label: string }> = [
  { value: "all", label: "All" },
  { value: "pending", label: "Pending" },
  { value: "processing", label: "Active" },
  { value: "completed", label: "Done" },
  { value: "failed", label: "Failed" },
  { value: "retrying", label: "Retrying" },
  { value: "dead_letter", label: "DLQ" },
];

interface JobStatusTabsProps {
  value: JobStatus | "all";
  onChange: (value: JobStatus | "all") => void;
}

export function JobStatusTabs({ value, onChange }: JobStatusTabsProps) {
  return (
    <div className="flex gap-1 overflow-x-auto border-b border-border pb-px scrollbar-none">
      {TABS.map((tab) => (
        <button
          key={tab.value}
          onClick={() => onChange(tab.value)}
          className={`whitespace-nowrap px-3 py-2 text-xs font-mono uppercase tracking-wider transition-colors cursor-pointer ${
            value === tab.value
              ? "border-b-2 border-primary text-foreground"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
