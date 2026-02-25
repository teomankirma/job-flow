import { JobDetail } from "@/components/jobs/job-detail";

interface JobDetailPageProps {
  params: Promise<{ id: string }>;
}

export default async function JobDetailPage({ params }: JobDetailPageProps) {
  const { id } = await params;
  return <JobDetail jobId={id} />;
}
