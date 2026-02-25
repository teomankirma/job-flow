"use client";

import { Button } from "@/components/ui/button";
import { useRetryJob } from "@/lib/api/hooks";
import { toast } from "sonner";
import type { JobStatus } from "@/lib/types";

interface RetryButtonProps {
  jobId: string;
  status: JobStatus;
  size?: "sm" | "default";
}

export function RetryButton({ jobId, status, size = "sm" }: RetryButtonProps) {
  const { mutate, isPending } = useRetryJob();

  if (status !== "failed" && status !== "dead_letter") return null;

  return (
    <Button
      variant="outline"
      size={size}
      disabled={isPending}
      onClick={(e) => {
        e.stopPropagation();
        mutate(jobId, {
          onSuccess: () => toast.success("Job re-queued for processing"),
          onError: (err) => toast.error(`Retry failed: ${err.message}`),
        });
      }}
      className="font-mono text-xs uppercase tracking-wider"
    >
      {isPending ? "Retrying..." : "Retry"}
    </Button>
  );
}
