"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useCreateJob } from "@/lib/api/hooks";
import { JOB_TYPE_CONFIG, type JobType } from "@/lib/types";
import { toast } from "sonner";
import { motion } from "motion/react";
import { slideUp } from "@/lib/motion";

const JOB_TYPES = Object.entries(JOB_TYPE_CONFIG) as [
  JobType,
  (typeof JOB_TYPE_CONFIG)[JobType],
][];

const DEFAULT_PAYLOADS: Record<JobType, string> = {
  "email.send": JSON.stringify(
    { to: "user@example.com", subject: "Hello", body: "Test email" },
    null,
    2,
  ),
  "report.generate": JSON.stringify(
    { report_type: "monthly", format: "pdf" },
    null,
    2,
  ),
  "image.process": JSON.stringify(
    { url: "https://example.com/image.png", width: 800 },
    null,
    2,
  ),
};

export function CreateJobForm() {
  const router = useRouter();
  const { mutate, isPending } = useCreateJob();

  const [jobType, setJobType] = useState<JobType>("email.send");
  const [payload, setPayload] = useState(DEFAULT_PAYLOADS["email.send"]);
  const [maxAttempts, setMaxAttempts] = useState(3);
  const [payloadError, setPayloadError] = useState<string | null>(null);

  const handleTypeChange = (type: JobType) => {
    setJobType(type);
    setPayload(DEFAULT_PAYLOADS[type]);
    setPayloadError(null);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    let parsedPayload: Record<string, unknown>;
    try {
      parsedPayload = JSON.parse(payload);
    } catch {
      setPayloadError("Invalid JSON payload");
      return;
    }

    mutate(
      { type: jobType, payload: parsedPayload, max_attempts: maxAttempts },
      {
        onSuccess: (job) => {
          toast.success("Job created successfully");
          router.push(`/jobs/${job.id}`);
        },
        onError: (err) => {
          toast.error(`Failed to create job: ${err.message}`);
        },
      },
    );
  };

  return (
    <motion.div variants={slideUp} initial="hidden" animate="visible">
      <Card>
        <CardHeader>
          <CardTitle className="font-mono text-sm uppercase tracking-widest">
            Job Configuration
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label
                htmlFor="type"
                className="font-mono text-xs uppercase tracking-wider"
              >
                Job Type
              </Label>
              <Select
                value={jobType}
                onValueChange={(v) => handleTypeChange(v as JobType)}
              >
                <SelectTrigger className="font-mono">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {JOB_TYPES.map(([value, config]) => (
                    <SelectItem key={value} value={value} className="font-mono">
                      <div>
                        <div className="text-sm">{config.label}</div>
                        <div className="text-xs text-muted-foreground">
                          {config.description}
                        </div>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label
                htmlFor="payload"
                className="font-mono text-xs uppercase tracking-wider"
              >
                Payload (JSON)
              </Label>
              <Textarea
                id="payload"
                value={payload}
                onChange={(e) => {
                  setPayload(e.target.value);
                  setPayloadError(null);
                }}
                rows={6}
                className="font-mono text-sm"
                placeholder='{"key": "value"}'
              />
              {payloadError && (
                <p className="text-xs text-destructive font-mono">
                  {payloadError}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label
                htmlFor="max_attempts"
                className="font-mono text-xs uppercase tracking-wider"
              >
                Max Attempts
              </Label>
              <Input
                id="max_attempts"
                type="number"
                min={1}
                max={10}
                value={maxAttempts}
                onChange={(e) => setMaxAttempts(Number(e.target.value))}
                className="font-mono w-24"
              />
            </div>

            <Button
              type="submit"
              disabled={isPending}
              className="w-full font-mono uppercase tracking-widest"
            >
              {isPending ? "Creating..." : "Submit Job"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </motion.div>
  );
}
