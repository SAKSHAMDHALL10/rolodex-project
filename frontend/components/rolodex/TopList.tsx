import type { TopCount } from "@/types";

export function TopList({ title, items }: { title: string; items: TopCount[] }) {
  const max = items[0]?.count ?? 1;

  return (
    <div className="rounded-card border border-hairline bg-surface p-5 shadow-card">
      <h3 className="font-display text-sm font-medium text-ink">{title}</h3>
      {items.length === 0 ? (
        <p className="mt-4 text-sm text-ink-faint">Nothing here yet.</p>
      ) : (
        <ul className="mt-4 flex flex-col gap-2.5">
          {items.map((item) => (
            <li key={item.name} className="flex items-center gap-3">
              <span className="w-24 shrink-0 truncate text-sm text-ink-muted" title={item.name}>
                {item.name}
              </span>
              <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-surface-raised">
                <div
                  className="h-full rounded-full bg-signal"
                  style={{ width: `${Math.max((item.count / max) * 100, 6)}%` }}
                />
              </div>
              <span className="w-6 shrink-0 text-right font-mono text-xs text-ink-faint">
                {item.count}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
