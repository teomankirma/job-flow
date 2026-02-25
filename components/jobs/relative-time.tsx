"use client";

import { useState, useEffect } from "react";
import { formatRelativeTime } from "@/lib/utils/format";

export function RelativeTime({ date }: { date: string }) {
  const [text, setText] = useState(() => formatRelativeTime(date));

  useEffect(() => {
    const id = setInterval(() => setText(formatRelativeTime(date)), 1000);
    return () => clearInterval(id);
  }, [date]);

  return <>{text}</>;
}
