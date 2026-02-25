"use client";

import { Button } from "@/components/ui/button";

interface JobPaginationProps {
  total: number;
  pageSize: number;
  currentPage: number;
  onPageChange: (page: number) => void;
}

export function JobPagination({
  total,
  pageSize,
  currentPage,
  onPageChange,
}: JobPaginationProps) {
  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="flex items-center justify-between border-t border-border pt-4">
      <span className="font-mono text-xs text-muted-foreground">
        Page {currentPage + 1} of {totalPages}
      </span>
      <div className="flex gap-1">
        <Button
          variant="outline"
          size="sm"
          disabled={currentPage === 0}
          onClick={() => onPageChange(currentPage - 1)}
          className="font-mono text-xs"
        >
          Prev
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={currentPage >= totalPages - 1}
          onClick={() => onPageChange(currentPage + 1)}
          className="font-mono text-xs"
        >
          Next
        </Button>
      </div>
    </div>
  );
}
