import { request } from "./client";
import type { Job, JobListResponse, CreateJobRequest } from "@/lib/types";

export async function listJobs(params?: {
  limit?: number;
  offset?: number;
  status?: string;
}): Promise<JobListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.set("limit", String(params.limit));
  if (params?.offset) searchParams.set("offset", String(params.offset));
  if (params?.status) searchParams.set("status", params.status);

  const query = searchParams.toString();
  return request<JobListResponse>(`/jobs${query ? `?${query}` : ""}`);
}

export async function getJob(id: string): Promise<Job> {
  return request<Job>(`/jobs/${id}`);
}

export async function createJob(
  data: CreateJobRequest,
  idempotencyKey?: string,
): Promise<Job> {
  const headers: Record<string, string> = {};
  if (idempotencyKey) {
    headers["Idempotency-Key"] = idempotencyKey;
  }
  return request<Job>("/jobs", {
    method: "POST",
    headers,
    body: JSON.stringify(data),
  });
}

export async function retryJob(id: string): Promise<Job> {
  return request<Job>(`/jobs/${id}/retry`, { method: "POST" });
}
