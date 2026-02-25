"use client";

import { useRouter } from "next/navigation";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { StatusBadge } from "./status-badge";
import { JobTypeLabel } from "./job-type-label";
import { RetryButton } from "./retry-button";
import { RelativeTime } from "./relative-time";
import { truncateId } from "@/lib/utils/format";
import type { Job } from "@/lib/types";

interface JobTableProps {
  jobs: Job[];
}

export function JobTable({ jobs }: JobTableProps) {
  const router = useRouter();

  return (
    <div className="border border-border">
      <Table>
        <TableHeader>
          <TableRow className="border-border hover:bg-transparent">
            <TableHead className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
              ID
            </TableHead>
            <TableHead className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
              Type
            </TableHead>
            <TableHead className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
              Status
            </TableHead>
            <TableHead className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
              Attempts
            </TableHead>
            <TableHead className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
              Created
            </TableHead>
            <TableHead className="font-mono text-xs uppercase tracking-wider text-muted-foreground w-[80px]">
              Actions
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {jobs.map((job) => (
            <TableRow
              key={job.id}
              onClick={() => router.push(`/jobs/${job.id}`)}
              className="cursor-pointer border-b border-border transition-colors hover:bg-secondary/50"
            >
              <TableCell className="font-mono text-xs text-muted-foreground">
                {truncateId(job.id)}
              </TableCell>
              <TableCell>
                <JobTypeLabel type={job.type} />
              </TableCell>
              <TableCell>
                <StatusBadge status={job.status} />
              </TableCell>
              <TableCell className="font-mono text-xs">
                {job.attempts}/{job.max_attempts}
              </TableCell>
              <TableCell className="font-mono text-xs text-muted-foreground">
                <RelativeTime date={job.created_at} />
              </TableCell>
              <TableCell>
                <div className="flex items-center h-6">
                  <RetryButton jobId={job.id} status={job.status} />
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
