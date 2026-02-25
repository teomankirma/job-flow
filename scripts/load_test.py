#!/usr/bin/env python3
"""Load test script: enqueue jobs and optionally watch processing metrics."""

import argparse
import asyncio
import random
import time

import httpx

EMAIL_PAYLOADS = [
    {"to": "alice@example.com", "subject": "Welcome aboard"},
    {"to": "bob@example.com", "subject": "Your invoice is ready"},
    {"to": "carol@example.com", "subject": "Password reset request"},
    {"to": "dave@example.com", "subject": "Weekly digest"},
    {"to": "eve@example.com", "subject": "Order confirmation"},
]

REPORT_PAYLOADS = [
    {"report_type": "monthly", "format": "pdf"},
    {"report_type": "quarterly", "format": "csv"},
    {"report_type": "annual", "format": "pdf"},
    {"report_type": "daily", "format": "json"},
    {"report_type": "weekly", "format": "xlsx"},
]

CONCURRENCY = 50


async def enqueue_job(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    url: str,
    index: int,
    total: int,
    stats: dict,
):
    """Enqueue a single job, handling rate limiting with backoff."""
    if random.random() < 0.6:
        job_type = "email.send"
        payload = random.choice(EMAIL_PAYLOADS)
    else:
        job_type = "report.generate"
        payload = random.choice(REPORT_PAYLOADS)

    body = {"type": job_type, "payload": payload, "max_attempts": 3}

    async with semaphore:
        for attempt in range(5):
            try:
                resp = await client.post(f"{url}/jobs", json=body)
                if resp.status_code == 429:
                    retry_after = float(resp.headers.get("retry-after", "2"))
                    await asyncio.sleep(retry_after)
                    continue
                resp.raise_for_status()
                job_id = resp.json()["id"][:8]
                stats["ok"] += 1
                print(f"  [{stats['ok'] + stats['fail']}/{total}] {job_type} → {job_id}")
                return
            except httpx.HTTPError:
                await asyncio.sleep(0.5 * (attempt + 1))

        stats["fail"] += 1
        print(f"  [{stats['ok'] + stats['fail']}/{total}] FAILED {job_type}")


async def poll_metrics(client: httpx.AsyncClient, url: str):
    """Poll /metrics until queue is drained and no active jobs remain."""
    print("\nWatching metrics (Ctrl+C to stop)...\n")
    header = f"  {'total':>7} {'active':>7} {'done':>7} {'failed':>7} {'dlq':>7} {'queue':>7} {'retry':>7}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    while True:
        try:
            resp = await client.get(f"{url}/metrics")
            m = resp.json()
            print(
                f"  {m['total_jobs']:>7} {m['active_jobs']:>7} "
                f"{m['completed_jobs']:>7} {m['failed_jobs']:>7} "
                f"{m['dead_letter_jobs']:>7} {m['queue_length']:>7} "
                f"{m['retry_queue_length']:>7}",
                end="\r",
            )

            if (
                m["queue_length"] == 0
                and m["retry_queue_length"] == 0
                and m["active_jobs"] == 0
            ):
                print()
                print(
                    f"\nAll jobs processed: {m['completed_jobs']} completed, "
                    f"{m['failed_jobs']} failed, {m['dead_letter_jobs']} dead-lettered"
                )
                break
        except httpx.HTTPError:
            pass

        await asyncio.sleep(2)


async def main():
    parser = argparse.ArgumentParser(description="Job Flow load test")
    parser.add_argument(
        "--url", default="http://localhost:8000", help="API base URL"
    )
    parser.add_argument(
        "--count", type=int, default=1000, help="Number of jobs to enqueue"
    )
    parser.add_argument(
        "--poll", action="store_true", help="Poll metrics after enqueue"
    )
    args = parser.parse_args()

    print(f"Enqueuing {args.count} jobs to {args.url}...\n")

    stats = {"ok": 0, "fail": 0}
    semaphore = asyncio.Semaphore(CONCURRENCY)
    start = time.perf_counter()

    async with httpx.AsyncClient(timeout=30) as client:
        tasks = [
            enqueue_job(client, semaphore, args.url, i, args.count, stats)
            for i in range(args.count)
        ]
        await asyncio.gather(*tasks)

        elapsed = time.perf_counter() - start
        rate = stats["ok"] / elapsed if elapsed > 0 else 0

        print(f"\nDone in {elapsed:.1f}s — {stats['ok']} enqueued, {stats['fail']} failed ({rate:.1f} jobs/s)")

        if args.poll:
            await poll_metrics(client, args.url)


if __name__ == "__main__":
    asyncio.run(main())
