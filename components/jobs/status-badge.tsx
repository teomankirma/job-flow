import { Badge } from "@/components/ui/badge";
import { JOB_STATUS_CONFIG, type JobStatus } from "@/lib/types";

interface StatusBadgeProps {
  status: JobStatus;
}

const STATUS_CSS_VAR: Record<JobStatus, string> = {
  pending: "var(--status-pending)",
  processing: "var(--status-processing)",
  completed: "var(--status-completed)",
  failed: "var(--status-failed)",
  retrying: "var(--status-retrying)",
  dead_letter: "var(--status-dead-letter)",
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = JOB_STATUS_CONFIG[status];

  return (
    <Badge variant={status}>
      <span
        className={`mr-1 inline-block h-1.5 w-1.5 shrink-0 ${
          status === "processing" ? "animate-pulse-glow" : ""
        }`}
        style={{ backgroundColor: STATUS_CSS_VAR[status] }}
      />
      {config.label}
    </Badge>
  );
}
