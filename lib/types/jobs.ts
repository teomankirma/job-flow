export type JobStatus =
  | "pending"
  | "processing"
  | "completed"
  | "failed"
  | "retrying"
  | "dead_letter";

export type JobType = "email.send" | "report.generate" | "image.process";

export interface Job {
  id: string;
  type: JobType;
  payload: Record<string, unknown>;
  status: JobStatus;
  attempts: number;
  max_attempts: number;
  error_message: string | null;
  idempotency_key: string | null;
  created_at: string;
  updated_at: string;
}

export interface JobListResponse {
  items: Job[];
  total: number;
  limit: number;
  offset: number;
}

export interface CreateJobRequest {
  type: JobType;
  payload: Record<string, unknown>;
  max_attempts: number;
}

export const JOB_STATUS_CONFIG: Record<
  JobStatus,
  { label: string; variant: JobStatus }
> = {
  pending: { label: "Pending", variant: "pending" },
  processing: { label: "Processing", variant: "processing" },
  completed: { label: "Completed", variant: "completed" },
  failed: { label: "Failed", variant: "failed" },
  retrying: { label: "Retrying", variant: "retrying" },
  dead_letter: { label: "Dead Letter", variant: "dead_letter" },
};

export const JOB_TYPE_CONFIG: Record<
  JobType,
  { label: string; description: string }
> = {
  "email.send": {
    label: "Email Send",
    description: "Simulate sending an email notification",
  },
  "report.generate": {
    label: "Report Generate",
    description: "Generate a report (may fail randomly)",
  },
  "image.process": {
    label: "Image Process",
    description: "Process an image (heavy simulation)",
  },
};
