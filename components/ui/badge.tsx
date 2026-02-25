import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { Slot } from "radix-ui"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center justify-center border px-2 py-0.5 text-xs font-mono font-medium uppercase tracking-wider w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none transition-[color,box-shadow] overflow-hidden",
  {
    variants: {
      variant: {
        default: "bg-primary/10 text-primary border-primary/30",
        secondary:
          "bg-secondary text-secondary-foreground border-secondary",
        destructive:
          "bg-destructive/10 text-destructive border-destructive/30",
        outline:
          "border-border text-foreground",
        pending:
          "border-status-pending/30 bg-status-pending/10 text-status-pending",
        processing:
          "border-status-processing/30 bg-status-processing/10 text-status-processing animate-pulse-glow",
        completed:
          "border-status-completed/30 bg-status-completed/10 text-status-completed",
        failed:
          "border-status-failed/30 bg-status-failed/10 text-status-failed",
        retrying:
          "border-status-retrying/30 bg-status-retrying/10 text-status-retrying",
        dead_letter:
          "border-status-dead-letter/30 bg-status-dead-letter/10 text-status-dead-letter",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

function Badge({
  className,
  variant = "default",
  asChild = false,
  ...props
}: React.ComponentProps<"span"> &
  VariantProps<typeof badgeVariants> & { asChild?: boolean }) {
  const Comp = asChild ? Slot.Root : "span"

  return (
    <Comp
      data-slot="badge"
      data-variant={variant}
      className={cn(badgeVariants({ variant }), className)}
      {...props}
    />
  )
}

export { Badge, badgeVariants }
