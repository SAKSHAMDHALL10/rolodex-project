import { forwardRef } from "react";
import { cn } from "@/lib/utils";

export const Textarea = forwardRef<HTMLTextAreaElement, React.TextareaHTMLAttributes<HTMLTextAreaElement>>(
  ({ className, ...props }, ref) => (
    <textarea
      ref={ref}
      className={cn(
        "w-full rounded-card border border-hairline bg-surface px-4 py-3 text-sm text-ink placeholder:text-ink-faint",
        "focus:outline-none focus-visible:outline-2 focus-visible:outline-signal",
        className
      )}
      {...props}
    />
  )
);
Textarea.displayName = "Textarea";

export const Input = forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "w-full rounded-tab border border-hairline bg-surface px-3.5 py-2.5 text-sm text-ink placeholder:text-ink-faint",
        "focus:outline-none focus-visible:outline-2 focus-visible:outline-signal",
        className
      )}
      {...props}
    />
  )
);
Input.displayName = "Input";
