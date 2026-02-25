import type { Metadata } from "next";
import { AboutContent } from "@/components/about/about-content";

export const metadata: Metadata = {
  title: "Job Flow — Distributed Job Processing System",
  description:
    "A distributed background job processing system with retry logic, dead-letter queues, and a real-time dashboard. Built with FastAPI, Redis, PostgreSQL, and Next.js.",
};

export default function HomePage() {
  return <AboutContent />;
}
