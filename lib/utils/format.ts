function parseUTC(isoString: string): Date {
  // API returns naive UTC timestamps without Z suffix — force UTC interpretation
  const s = isoString.endsWith("Z") ? isoString : isoString + "Z";
  return new Date(s);
}

export function formatRelativeTime(isoString: string): string {
  const date = parseUTC(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.max(0, Math.floor(diffMs / 1000));

  if (diffSecs < 60) return `${diffSecs}s ago`;
  const diffMins = Math.floor(diffSecs / 60);
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

export function formatDateTime(isoString: string): string {
  return parseUTC(isoString).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

export function truncateId(id: string): string {
  return id.slice(0, 8);
}

export function generateIdempotencyKey(): string {
  return crypto.randomUUID();
}
