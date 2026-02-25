"use client";

import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { m } from "motion/react";
import { fadeIn, slideUp } from "@/lib/motion";
import {
  Zap,
  RotateCcw,
  Archive,
  Key,
  Shield,
  Activity,
  BarChart3,
  Power,
} from "lucide-react";

const BACKEND_STACK = [
  "Python 3.12",
  "FastAPI",
  "SQLAlchemy 2.0",
  "PostgreSQL 17",
  "Redis 7",
  "Alembic",
];

const FRONTEND_STACK = [
  "Next.js 16",
  "TypeScript",
  "Tailwind CSS v4",
  "TanStack Query",
  "Framer Motion",
  "shadcn/ui",
];

const INFRA_STACK = ["Docker Compose", "Structured JSON Logging", "asyncio"];

const FEATURES = [
  {
    icon: Zap,
    title: "Async Job Processing",
    description:
      "Redis-backed queue with BLPOP and asyncio workers processing jobs concurrently via semaphore.",
  },
  {
    icon: RotateCcw,
    title: "Retry with Backoff",
    description:
      "Failed jobs retry with exponential backoff (2^attempts seconds) using a Redis Sorted Set.",
  },
  {
    icon: Archive,
    title: "Dead-Letter Queue",
    description:
      "Jobs exceeding max attempts are moved to a DLQ for manual inspection and retry.",
  },
  {
    icon: Key,
    title: "Idempotency",
    description:
      "Idempotency-Key header prevents duplicate job creation with race condition handling.",
  },
  {
    icon: Shield,
    title: "Rate Limiting",
    description:
      "Sliding-window rate limiter using Redis ZSET pipeline. POST-only to avoid blocking reads.",
  },
  {
    icon: Activity,
    title: "Real-time Dashboard",
    description:
      "Next.js frontend with 2s polling, URL-persisted filters, and responsive table/card views.",
  },
  {
    icon: BarChart3,
    title: "Metrics Endpoint",
    description:
      "Queue sizes, job counts by status, and failure tracking via a single API call.",
  },
  {
    icon: Power,
    title: "Graceful Shutdown",
    description:
      "Workers drain in-flight jobs on SIGTERM. No dropped work during deployments.",
  },
];

const ARCHITECTURE = `+-----------+       +-----------+       +-----------+
|  Next.js  | ----> |  FastAPI  | ----> |  Worker   |
|   :3000   | <---- |   :8000   |       | (asyncio) |
+-----------+       +-----+-----+       +-----+-----+
                          |                   |
                    +-----v-----+       +-----v-----+
                    |  Postgres | <---- |   Redis   |
                    |   :5432   |       |   :6379   |
                    +-----------+       +-----------+
                                        | job_queue |
                                        | retry_q   |
                                        | dlq       |
                                        +-----------+`;

export function AboutContent() {
  return (
    <m.div
      variants={fadeIn}
      initial="hidden"
      animate="visible"
      className="space-y-10"
    >
      {/* Hero */}
      <div className="space-y-3">
        <h1 className="font-mono text-2xl font-bold uppercase tracking-widest sm:text-3xl">
          Job Flow
        </h1>
        <p className="max-w-2xl text-muted-foreground">
          A distributed background job processing system with retry logic,
          dead-letter queues, and a real-time dashboard. Built to demonstrate
          production-grade async architecture, fault tolerance, and full-stack
          integration.
        </p>
        <div className="flex gap-2 pt-2">
          <Link href="/dashboard">
            <Button className="font-mono text-xs uppercase tracking-widest">
              Open Dashboard
            </Button>
          </Link>
          <Link href="/create">
            <Button
              variant="outline"
              className="font-mono text-xs uppercase tracking-widest"
            >
              Create Job
            </Button>
          </Link>
        </div>
      </div>

      {/* Tech Stack */}
      <m.div variants={slideUp} initial="hidden" animate="visible">
        <h2 className="mb-4 font-mono text-sm font-bold uppercase tracking-widest">
          Tech Stack
        </h2>
        <div className="grid gap-3 md:grid-cols-3">
          <Card className="py-3 gap-0">
            <CardContent className="px-4">
              <p className="mb-2 font-mono text-xs uppercase tracking-wider text-muted-foreground">
                Backend
              </p>
              <div className="flex flex-wrap gap-1.5">
                {BACKEND_STACK.map((tech) => (
                  <Badge key={tech} variant="secondary" className="text-xs">
                    {tech}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
          <Card className="py-3 gap-0">
            <CardContent className="px-4">
              <p className="mb-2 font-mono text-xs uppercase tracking-wider text-muted-foreground">
                Frontend
              </p>
              <div className="flex flex-wrap gap-1.5">
                {FRONTEND_STACK.map((tech) => (
                  <Badge key={tech} variant="secondary" className="text-xs">
                    {tech}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
          <Card className="py-3 gap-0">
            <CardContent className="px-4">
              <p className="mb-2 font-mono text-xs uppercase tracking-wider text-muted-foreground">
                Infrastructure
              </p>
              <div className="flex flex-wrap gap-1.5">
                {INFRA_STACK.map((tech) => (
                  <Badge key={tech} variant="secondary" className="text-xs">
                    {tech}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </m.div>

      {/* Features */}
      <m.div
        variants={slideUp}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.1 }}
      >
        <h2 className="mb-4 font-mono text-sm font-bold uppercase tracking-widest">
          Key Features
        </h2>
        <div className="grid gap-3 sm:grid-cols-2">
          {FEATURES.map((feature) => (
            <Card key={feature.title} className="py-3 gap-0">
              <CardContent className="flex gap-3 px-4">
                <feature.icon className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                <div>
                  <p className="font-mono text-xs font-medium uppercase tracking-wider">
                    {feature.title}
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </m.div>

      {/* Architecture */}
      <m.div
        variants={slideUp}
        initial="hidden"
        animate="visible"
        transition={{ delay: 0.2 }}
      >
        <h2 className="mb-4 font-mono text-sm font-bold uppercase tracking-widest">
          Architecture
        </h2>
        <pre className="overflow-x-auto border border-border bg-secondary p-4 font-mono text-xs leading-relaxed text-foreground">
          {ARCHITECTURE}
        </pre>
      </m.div>
    </m.div>
  );
}
