import { Badge } from "@/components/ui/badge";
import { JOB_STATUS_CONFIG, type JobStatus } from "@/lib/types";

interface StatusBadgeProps {
  status: JobStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = JOB_STATUS_CONFIG[status];

  return (
    <span className="inline-flex w-28">
      <Badge variant={status} className="flex-1 text-center px-0">
        {config.label}
      </Badge>
    </span>
  );
}
