import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

export function StatCard({
  label,
  value,
  icon: Icon,
  accent = false,
}: {
  label: string;
  value: string | number;
  icon: LucideIcon;
  accent?: boolean;
}) {
  return (
    <div className="rounded-card border border-hairline bg-surface p-5 shadow-card">
      <div className="flex items-center justify-between">
        <span className="text-xs uppercase tracking-wide text-ink-muted">{label}</span>
        <Icon size={16} className={cn(accent ? "text-signal" : "text-ink-faint")} />
      </div>
      <p className="mt-3 font-mono text-3xl font-medium text-ink">{value}</p>
    </div>
  );
}
