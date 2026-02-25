import { JOB_TYPE_CONFIG, type JobType } from "@/lib/types";

interface JobTypeLabelProps {
  type: JobType;
}

export function JobTypeLabel({ type }: JobTypeLabelProps) {
  const config = JOB_TYPE_CONFIG[type];
  return (
    <span className="font-mono text-sm text-foreground">
      {config?.label ?? type}
    </span>
  );
}
