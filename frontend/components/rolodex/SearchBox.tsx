"use client";

import { useState } from "react";
import { Search, Loader2, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

const EXAMPLES = [
  "Who has built AI agents in production?",
  "Who do we know with startup hiring experience?",
  "Who knows Kubernetes and distributed systems?",
  "Who has healthcare or regulatory experience?",
];

export function SearchBox({
  onSearch,
  loading = false,
  size = "lg",
}: {
  onSearch: (query: string) => void;
  loading?: boolean;
  size?: "lg" | "md";
}) {
  const [value, setValue] = useState("");

  function submit(q?: string) {
    const query = (q ?? value).trim();
    if (!query) return;
    onSearch(query);
  }

  return (
    <div className="w-full">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
        className={cn(
          "flex items-center gap-3 rounded-card border border-hairline bg-surface px-4 shadow-card transition-shadow focus-within:shadow-signal-glow",
          size === "lg" ? "py-4" : "py-2.5"
        )}
      >
        <Sparkles size={18} className="shrink-0 text-signal" />
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Ask anything — “who has healthcare experience?”"
          className={cn(
            "flex-1 bg-transparent text-ink placeholder:text-ink-faint focus:outline-none",
            size === "lg" ? "text-base" : "text-sm"
          )}
        />
        <button
          type="submit"
          disabled={loading}
          aria-label="Search"
          className="flex shrink-0 items-center gap-1.5 rounded-tab bg-signal px-3.5 py-1.5 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-60"
        >
          {loading ? <Loader2 size={14} className="animate-spin" /> : <Search size={14} />}
          Search
        </button>
      </form>

      {size === "lg" && (
        <div className="mt-3 flex flex-wrap gap-2">
          {EXAMPLES.map((example) => (
            <button
              key={example}
              onClick={() => {
                setValue(example);
                submit(example);
              }}
              className="rounded-tab border border-hairline px-3 py-1.5 font-mono text-xs text-ink-muted transition-colors hover:border-signal/40 hover:text-ink"
            >
              {example}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
