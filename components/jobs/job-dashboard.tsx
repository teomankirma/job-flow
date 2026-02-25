"use client";

import { useState } from "react";
import { useJobs } from "@/lib/api/hooks";
import { JobStatusTabs } from "./job-status-tabs";
import { JobTable } from "./job-table";
import { JobCardList } from "./job-card-list";
import { JobPagination } from "./job-pagination";
import { DashboardSkeleton } from "./dashboard-skeleton";
import { motion } from "motion/react";
import { fadeIn } from "@/lib/motion";
import type { JobStatus } from "@/lib/types";

const PAGE_SIZE = 20;

export function JobDashboard() {
  const [statusFilter, setStatusFilter] = useState<JobStatus | "all">("all");
  const [page, setPage] = useState(0);

  const { data, isLoading, isPlaceholderData, isError, error } = useJobs({
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
    status: statusFilter === "all" ? undefined : statusFilter,
  });

  const handleFilterChange = (status: JobStatus | "all") => {
    setStatusFilter(status);
    setPage(0);
  };

  return (
    <motion.div
      variants={fadeIn}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-mono text-lg font-bold uppercase tracking-widest">
            Job Queue
          </h1>
          <p className="text-xs text-muted-foreground font-mono">
            {data ? `${data.total} total jobs` : "Loading..."}
          </p>
        </div>
      </div>

      <JobStatusTabs value={statusFilter} onChange={handleFilterChange} />

      {isLoading ? (
        <DashboardSkeleton />
      ) : isError ? (
        <div className="border border-destructive/30 bg-destructive/5 p-4">
          <p className="font-mono text-sm text-destructive">
            Error: {error?.message ?? "Failed to load jobs"}
          </p>
        </div>
      ) : data && data.items.length > 0 ? (
        <div className={`transition-opacity duration-200 ${isPlaceholderData ? "opacity-50" : "opacity-100"}`}>
          <div className="hidden md:block">
            <JobTable jobs={data.items} />
          </div>
          <div className="md:hidden">
            <JobCardList jobs={data.items} />
          </div>

          {data.total > PAGE_SIZE && (
            <JobPagination
              total={data.total}
              pageSize={PAGE_SIZE}
              currentPage={page}
              onPageChange={setPage}
            />
          )}
        </div>
      ) : (
        <div className="border border-border bg-card p-8 text-center">
          <p className="font-mono text-sm text-muted-foreground">
            No jobs found. Create one to get started.
          </p>
        </div>
      )}
    </motion.div>
  );
}
