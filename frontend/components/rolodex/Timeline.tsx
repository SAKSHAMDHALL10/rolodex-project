import type { EducationItem, ExperienceItem } from "@/types";

export function ExperienceTimeline({ items }: { items: ExperienceItem[] }) {
  if (items.length === 0) return null;

  return (
    <ol className="relative border-l border-hairline pl-6">
      {items.map((item, i) => (
        <li key={`${item.company}-${i}`} className="mb-7 last:mb-0">
          <span className="absolute -left-[5px] mt-1.5 h-2.5 w-2.5 rounded-full border-2 border-canvas bg-signal" />
          <div className="flex flex-wrap items-baseline justify-between gap-x-3">
            <h4 className="font-display text-sm font-medium text-ink">{item.title}</h4>
            <span className="font-mono text-xs text-ink-faint">
              {item.start_date ?? "—"} – {item.end_date ?? "Present"}
            </span>
          </div>
          <p className="text-sm text-ink-muted">{item.company}</p>
          {item.description && (
            <p className="mt-1.5 text-sm leading-relaxed text-ink-muted">{item.description}</p>
          )}
        </li>
      ))}
    </ol>
  );
}

export function EducationList({ items }: { items: EducationItem[] }) {
  if (items.length === 0) return null;

  return (
    <ul className="flex flex-col gap-3">
      {items.map((item, i) => (
        <li key={`${item.school}-${i}`}>
          <p className="text-sm font-medium text-ink">{item.school}</p>
          <p className="text-xs text-ink-muted">
            {[item.degree, item.field_of_study].filter(Boolean).join(", ")}
            {(item.start_year || item.end_year) && (
              <span className="font-mono text-ink-faint">
                {" · "}
                {item.start_year ?? "—"}–{item.end_year ?? "—"}
              </span>
            )}
          </p>
        </li>
      ))}
    </ul>
  );
}
