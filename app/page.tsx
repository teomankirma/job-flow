import { Suspense } from "react";
import { JobDashboard } from "@/components/jobs/job-dashboard";
import { DashboardSkeleton } from "@/components/jobs/dashboard-skeleton";

export default function DashboardPage() {
  return (
    <Suspense fallback={<DashboardSkeleton />}>
      <JobDashboard />
    </Suspense>
  );
}
