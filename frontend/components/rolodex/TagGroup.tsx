import { cn } from "@/lib/utils";

export function TagGroup({
  title,
  tags,
  variant = "default",
}: {
  title: string;
  tags: string[];
  variant?: "default" | "signal";
}) {
  if (tags.length === 0) return null;

  return (
    <div>
      <h4 className="text-xs uppercase tracking-wide text-ink-faint">{title}</h4>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {tags.map((tag) => (
          <span
            key={tag}
            className={cn(
              "rounded-tab border px-2.5 py-1 font-mono text-xs",
              variant === "signal"
                ? "border-signal/30 bg-signal-soft text-signal-strong"
                : "border-hairline text-ink-muted"
            )}
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
}
