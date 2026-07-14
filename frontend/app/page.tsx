"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Users, Sparkles, Clock, TrendingUp } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import type { DashboardStats } from "@/types";
import { SearchBox } from "@/components/rolodex/SearchBox";
import { StatCard } from "@/components/rolodex/StatCard";
import { StatCardSkeleton, ContactCardSkeleton } from "@/components/rolodex/Skeletons";
import { ContactCard } from "@/components/rolodex/ContactCard";
import { TopList } from "@/components/rolodex/TopList";
import { EmptyState } from "@/components/rolodex/EmptyState";
import { useToast } from "@/hooks/useToast";

export default function DashboardPage() {
  const router = useRouter();
  const { push } = useToast();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryKey, setRetryKey] = useState(0);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api
      .dashboard()
      .then(setStats)
      .catch((err) => {
        const message =
          err instanceof ApiError
            ? err.message
            : "Couldn't reach the Rolodex API. Is the backend running?";
        setError(message);
        push(message, "error");
      })
      .finally(() => setLoading(false));
  }, [push, retryKey]);

  function handleSearch(query: string) {
    router.push(`/search?q=${encodeURIComponent(query)}`);
  }

  return (
    <div className="flex flex-col gap-10">
      <section>
        <p className="font-mono text-xs uppercase tracking-widest text-signal">Rolodex</p>
        <h1 className="mt-2 font-display text-3xl font-medium text-ink sm:text-4xl">
          Who do we know who does that?
        </h1>
        <p className="mt-2 max-w-xl text-ink-muted">
          Paste a LinkedIn profile, and it becomes a searchable entry in your team&apos;s
          knowledge base of professional relationships.
        </p>
        <div className="mt-6 max-w-2xl">
          <SearchBox onSearch={handleSearch} />
        </div>
      </section>

      {error && !loading && (
        <EmptyState
          icon={Sparkles}
          title="Backend not reachable"
          description={`${error} Start it with "docker compose up" or see the README for local setup.`}
          actionLabel="Try again"
          onAction={() => setRetryKey((k) => k + 1)}
        />
      )}

      {!error && (
        <>
          <section className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {loading || !stats ? (
              Array.from({ length: 4 }).map((_, i) => <StatCardSkeleton key={i} />)
            ) : (
              <>
                <StatCard label="Total contacts" value={stats.total_contacts} icon={Users} accent />
                <StatCard label="Top skill" value={stats.top_skills[0]?.name ?? "—"} icon={TrendingUp} />
                <StatCard
                  label="Top industry"
                  value={stats.top_industries[0]?.name ?? "—"}
                  icon={Sparkles}
                />
                <StatCard
                  label="Recent searches"
                  value={stats.recent_searches.length}
                  icon={Clock}
                />
              </>
            )}
          </section>

          <section>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-display text-lg font-medium text-ink">Recently added</h2>
            </div>
            {loading || !stats ? (
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                {Array.from({ length: 3 }).map((_, i) => (
                  <ContactCardSkeleton key={i} />
                ))}
              </div>
            ) : stats.recent_contacts.length === 0 ? (
              <EmptyState
                icon={Users}
                title="Your rolodex is empty"
                description="Paste your first LinkedIn profile to generate a searchable entry."
                actionLabel="Add your first contact"
                actionHref="/ingest"
              />
            ) : (
              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
                {stats.recent_contacts.map((contact, i) => (
                  <ContactCard key={contact.id} contact={contact} index={i} />
                ))}
              </div>
            )}
          </section>

          {stats && stats.total_contacts > 0 && (
            <section className="grid grid-cols-1 gap-5 sm:grid-cols-3">
              <TopList title="Top skills" items={stats.top_skills} />
              <TopList title="Top industries" items={stats.top_industries} />
              <TopList title="Top relevance tags" items={stats.top_tags} />
            </section>
          )}

          {stats && stats.recent_searches.length > 0 && (
            <section>
              <h2 className="mb-3 font-display text-lg font-medium text-ink">Recent searches</h2>
              <div className="flex flex-wrap gap-2">
                {stats.recent_searches.map((q) => (
                  <button
                    key={q}
                    onClick={() => handleSearch(q)}
                    className="rounded-tab border border-hairline px-3 py-1.5 font-mono text-xs text-ink-muted hover:border-signal/40 hover:text-ink"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}
