"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertCircle, Contact2, Search } from "lucide-react";
import { api, describeApiError } from "@/lib/api";
import type { ContactListItem } from "@/types";
import { ContactCard } from "@/components/rolodex/ContactCard";
import { ContactGridSkeleton } from "@/components/rolodex/Skeletons";
import { EmptyState } from "@/components/rolodex/EmptyState";
import { Input } from "@/components/ui/Input";
import { useToast } from "@/hooks/useToast";

export default function ContactsPage() {
  const { push } = useToast();
  const [contacts, setContacts] = useState<ContactListItem[] | null>(null);
  const [loadError, setLoadError] = useState<{ title: string; description: string } | null>(
    null
  );
  const [filter, setFilter] = useState("");
  const [retryKey, setRetryKey] = useState(0);

  useEffect(() => {
    setLoadError(null);
    api.contacts
      .list({ limit: 200 })
      .then(setContacts)
      .catch((err) => {
        const described = describeApiError(err);
        push(described.description, "error");
        setLoadError(described);
      });
  }, [push, retryKey]);

  const filtered = useMemo(() => {
    if (!contacts) return [];
    const q = filter.trim().toLowerCase();
    if (!q) return contacts;
    return contacts.filter((c) =>
      [c.full_name, c.headline, c.current_company, c.current_title, ...c.relevance_tags]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(q)
    );
  }, [contacts, filter]);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-medium text-ink">All contacts</h1>
          <p className="mt-1 text-ink-muted">
            {contacts ? `${contacts.length} people in your rolodex` : "Loading…"}
          </p>
        </div>
        <div className="relative w-full max-w-xs">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-faint" />
          <Input
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filter by name, role, tag…"
            className="pl-9"
          />
        </div>
      </div>

      {loadError ? (
        <EmptyState
          icon={AlertCircle}
          title={loadError.title}
          description={loadError.description}
          actionLabel="Try again"
          onAction={() => setRetryKey((k) => k + 1)}
        />
      ) : !contacts ? (
        <ContactGridSkeleton count={9} />
      ) : contacts.length === 0 ? (
        <EmptyState
          icon={Contact2}
          title="Your rolodex is empty"
          description="Paste your first LinkedIn profile to generate a searchable entry."
          actionLabel="Add your first contact"
          actionHref="/ingest"
        />
      ) : filtered.length === 0 ? (
        <EmptyState icon={Search} title="No matches" description="Try a different filter term." />
      ) : (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((contact, i) => (
            <ContactCard key={contact.id} contact={contact} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}
