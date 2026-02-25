"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listJobs, getJob, createJob, retryJob } from "./jobs";
import type { CreateJobRequest } from "@/lib/types";
import { generateIdempotencyKey } from "@/lib/utils/format";

export const jobKeys = {
  all: ["jobs"] as const,
  lists: () => [...jobKeys.all, "list"] as const,
  list: (params: Record<string, unknown>) =>
    [...jobKeys.lists(), params] as const,
  details: () => [...jobKeys.all, "detail"] as const,
  detail: (id: string) => [...jobKeys.details(), id] as const,
};

export function useJobs(params?: {
  limit?: number;
  offset?: number;
  status?: string;
}) {
  return useQuery({
    queryKey: jobKeys.list(params ?? {}),
    queryFn: () => listJobs(params),
    refetchInterval: 2000,
  });
}

export function useJob(id: string) {
  return useQuery({
    queryKey: jobKeys.detail(id),
    queryFn: () => getJob(id),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "completed" || status === "dead_letter") return false;
      return 2000;
    },
  });
}

export function useCreateJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateJobRequest) =>
      createJob(data, generateIdempotencyKey()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: jobKeys.lists() });
    },
  });
}

export function useRetryJob() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => retryJob(id),
    onSuccess: (updatedJob) => {
      queryClient.setQueryData(jobKeys.detail(updatedJob.id), updatedJob);
      queryClient.invalidateQueries({ queryKey: jobKeys.lists() });
    },
  });
}
