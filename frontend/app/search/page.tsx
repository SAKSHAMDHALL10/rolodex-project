"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Search as SearchIcon, SlidersHorizontal, AlertCircle } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import type { SearchResponse } from "@/types";
import { SearchBox } from "@/components/rolodex/SearchBox";
import { ContactCard } from "@/components/rolodex/ContactCard";
import { ContactGridSkeleton } from "@/components/rolodex/Skeletons";
import { EmptyState } from "@/components/rolodex/EmptyState";
import { useToast } from "@/hooks/useToast";

function SearchPageInner() {
  const params = useSearchParams();
  const { push } = useToast();
  const [query, setQuery] = useState(params.get("q") ?? "");
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);

  async function runSearch(q: string) {
    setQuery(q);
    setLoading(true);
    setSearched(true);
    setSearchError(null);
    try {
      const res = await api.search.naturalLanguage(q);
      setResults(res);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Search failed. Is the backend running?";
      setSearchError(message);
      setResults(null);
      push(message, "error");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const initial = params.get("q");
    if (initial) runSearch(initial);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const activeFilters = results
    ? Object.entries(results.interpreted_filters).filter(([, v]) =>
        Array.isArray(v) ? v.length > 0 : Boolean(v)
      )
    : [];

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="font-display text-2xl font-medium text-ink">Search your rolodex</h1>
        <p className="mt-1 text-ink-muted">
          Ask in plain language — it&apos;s converted into filters and semantic search automatically.
        </p>
      </div>

      <SearchBox onSearch={runSearch} loading={loading} />

      {activeFilters.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 text-xs text-ink-muted">
          <SlidersHorizontal size={13} className="text-ink-faint" />
          <span>Interpreted as:</span>
          {activeFilters.map(([key, value]) => (
            <span
              key={key}
              className="rounded-tab border border-hairline px-2 py-1 font-mono text-[11px]"
            >
              {key}: {Array.isArray(value) ? value.join(", ") : String(value)}
            </span>
          ))}
        </div>
      )}

      {loading ? (
        <ContactGridSkeleton />
      ) : !searched ? (
        <EmptyState
          icon={SearchIcon}
          title="Search by role, skill, or plain-language relevance"
          description='Try "who has healthcare experience?" or "who knows Kubernetes?"'
        />
      ) : searchError ? (
        <EmptyState
          icon={AlertCircle}
          title="Search failed"
          description={searchError}
          actionLabel="Try again"
          onAction={() => runSearch(query)}
        />
      ) : results && results.results.length > 0 ? (
        <div>
          <p className="mb-3 text-sm text-ink-faint">
            {results.total} match{results.total === 1 ? "" : "es"} for &ldquo;{query}&rdquo;
          </p>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {results.results.map((r, i) => (
              <ContactCard
                key={r.contact.id}
                contact={r.contact}
                index={i}
                matchedTag={results.interpreted_filters.tags[0]}
              />
            ))}
          </div>
        </div>
      ) : (
        <EmptyState
          icon={SearchIcon}
          title="No matches"
          description="Try a broader query, or add more contacts to your rolodex."
          actionLabel="Add a contact"
          actionHref="/ingest"
        />
      )}
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<ContactGridSkeleton />}>
      <SearchPageInner />
    </Suspense>
  );
}
