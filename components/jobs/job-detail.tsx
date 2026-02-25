"use client";

import Link from "next/link";
import { useJob } from "@/lib/api/hooks";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "./status-badge";
import { JobTypeLabel } from "./job-type-label";
import { RetryButton } from "./retry-button";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDateTime } from "@/lib/utils/format";
import { motion } from "motion/react";
import { slideUp } from "@/lib/motion";

interface JobDetailProps {
  jobId: string;
}

export function JobDetail({ jobId }: JobDetailProps) {
  const { data: job, isLoading, isError, error } = useJob(jobId);

  if (isLoading) {
    return <JobDetailSkeleton />;
  }

  if (isError) {
    return (
      <div className="space-y-4">
        <BackButton />
        <div className="border border-destructive/30 bg-destructive/5 p-6">
          <p className="font-mono text-sm text-destructive">
            {error?.message ?? "Failed to load job"}
          </p>
        </div>
      </div>
    );
  }

  if (!job) return null;

  return (
    <motion.div
      variants={slideUp}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <BackButton />
        <RetryButton jobId={job.id} status={job.status} size="default" />
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="font-mono text-sm uppercase tracking-widest">
              Job Details
            </CardTitle>
            <StatusBadge status={job.status} />
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <DetailRow label="ID" value={job.id} mono />
          <DetailRow label="Type">
            <JobTypeLabel type={job.type} />
          </DetailRow>
          <DetailRow label="Status">
            <StatusBadge status={job.status} />
          </DetailRow>
          <DetailRow
            label="Attempts"
            value={`${job.attempts} / ${job.max_attempts}`}
            mono
          />
          <DetailRow
            label="Created"
            value={formatDateTime(job.created_at)}
            mono
          />
          <DetailRow
            label="Updated"
            value={formatDateTime(job.updated_at)}
            mono
          />
          {job.idempotency_key && (
            <DetailRow
              label="Idempotency Key"
              value={job.idempotency_key}
              mono
            />
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="font-mono text-sm uppercase tracking-widest">
            Payload
          </CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="overflow-x-auto bg-secondary p-4 font-mono text-xs text-foreground border border-border">
            {JSON.stringify(job.payload, null, 2)}
          </pre>
        </CardContent>
      </Card>

      {job.error_message && (
        <Card className="border-destructive/30">
          <CardHeader>
            <CardTitle className="font-mono text-sm uppercase tracking-widest text-destructive">
              Error
            </CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="overflow-x-auto bg-destructive/5 p-4 font-mono text-xs text-destructive border border-destructive/20">
              {job.error_message}
            </pre>
          </CardContent>
        </Card>
      )}
    </motion.div>
  );
}

function BackButton() {
  return (
    <Link href="/">
      <Button
        variant="ghost"
        size="sm"
        className="font-mono text-xs uppercase tracking-wider"
      >
        &larr; Back
      </Button>
    </Link>
  );
}

function DetailRow({
  label,
  value,
  mono,
  children,
}: {
  label: string;
  value?: string;
  mono?: boolean;
  children?: React.ReactNode;
}) {
  return (
    <div className="flex items-center justify-between border-b border-border pb-3 last:border-0 last:pb-0">
      <span className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
        {label}
      </span>
      {children ?? (
        <span className={`text-sm ${mono ? "font-mono" : ""}`}>{value}</span>
      )}
    </div>
  );
}

function JobDetailSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-8 w-32" />
      <Card>
        <CardContent className="space-y-4 pt-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="flex justify-between">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-4 w-40" />
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
