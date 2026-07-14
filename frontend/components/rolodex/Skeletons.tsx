export function ContactCardSkeleton() {
  return (
    <div className="rounded-card border border-hairline bg-surface p-5 pt-6">
      <div className="skeleton h-4 w-2/3 animate-shimmer rounded" />
      <div className="skeleton mt-2 h-3 w-1/2 animate-shimmer rounded" />
      <div className="mt-4 flex gap-3">
        <div className="skeleton h-3 w-16 animate-shimmer rounded" />
        <div className="skeleton h-3 w-16 animate-shimmer rounded" />
      </div>
      <div className="skeleton mt-4 h-6 w-3/4 animate-shimmer rounded" />
    </div>
  );
}

export function ContactGridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 gap-5 pt-3 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: count }).map((_, i) => (
        <ContactCardSkeleton key={i} />
      ))}
    </div>
  );
}

export function StatCardSkeleton() {
  return (
    <div className="rounded-card border border-hairline bg-surface p-5">
      <div className="skeleton h-3 w-20 animate-shimmer rounded" />
      <div className="skeleton mt-4 h-8 w-14 animate-shimmer rounded" />
    </div>
  );
}
