"use client";

import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { StatusBadge } from "./status-badge";
import { JobTypeLabel } from "./job-type-label";
import { RetryButton } from "./retry-button";
import { RelativeTime } from "./relative-time";
import { truncateId } from "@/lib/utils/format";
import type { Job } from "@/lib/types";

interface JobCardListProps {
  jobs: Job[];
}

export function JobCardList({ jobs }: JobCardListProps) {
  return (
    <div className="space-y-2">
      {jobs.map((job) => (
        <Link key={job.id} href={`/jobs/${job.id}`}>
          <Card className="transition-colors hover:bg-secondary/30 py-0">
            <CardContent className="flex items-center justify-between p-3">
              <div className="space-y-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs text-muted-foreground">
                    {truncateId(job.id)}
                  </span>
                  <StatusBadge status={job.status} />
                </div>
                <div className="flex items-center gap-3">
                  <JobTypeLabel type={job.type} />
                  <span className="font-mono text-xs text-muted-foreground">
                    {job.attempts}/{job.max_attempts}
                  </span>
                  <span className="font-mono text-xs text-muted-foreground">
                    <RelativeTime date={job.created_at} />
                  </span>
                </div>
              </div>
              <RetryButton jobId={job.id} status={job.status} />
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  );
}
