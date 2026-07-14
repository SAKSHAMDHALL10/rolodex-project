"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  Building2,
  ExternalLink,
  GraduationCap,
  MapPin,
  Trash2,
} from "lucide-react";
import { api, ApiError, describeApiError } from "@/lib/api";
import type { ContactRead } from "@/types";
import { initials } from "@/lib/utils";
import { ExperienceTimeline, EducationList } from "@/components/rolodex/Timeline";
import { TagGroup } from "@/components/rolodex/TagGroup";
import { ConnectionNotes } from "@/components/rolodex/ConnectionNotes";
import { Button } from "@/components/ui/Button";
import { useToast } from "@/hooks/useToast";

export default function ContactDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { push } = useToast();
  const [contact, setContact] = useState<ContactRead | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [loadError, setLoadError] = useState<{ title: string; description: string } | null>(
    null
  );
  const [retryKey, setRetryKey] = useState(0);

  useEffect(() => {
    setNotFound(false);
    setLoadError(null);
    api.contacts
      .get(params.id)
      .then(setContact)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 404) {
          setNotFound(true);
        } else {
          const described = describeApiError(err);
          setLoadError(described);
          push(described.description, "error");
        }
      });
  }, [params.id, retryKey, push]);

  async function handleAddNote(note: { note_type: string; text: string }) {
    if (!contact) return;
    try {
      const updated = await api.contacts.update(contact.id, {
        connection_notes: [
          { note_type: note.note_type, text: note.text, created_at: new Date().toISOString() },
        ],
      });
      setContact(updated);
      push("Note added.", "success");
    } catch {
      push("Couldn't save the note.", "error");
    }
  }

  async function handleDelete() {
    if (!contact) return;
    if (!window.confirm(`Remove ${contact.full_name} from your rolodex?`)) return;
    try {
      await api.contacts.remove(contact.id);
      push("Contact removed.", "success");
      router.push("/contacts");
    } catch {
      push("Couldn't remove this contact.", "error");
    }
  }

  if (notFound) {
    return (
      <div className="flex flex-col items-center py-20 text-center">
        <p className="font-display text-xl text-ink">Contact not found</p>
        <Link href="/contacts" className="mt-3 text-sm text-signal hover:underline">
          Back to all contacts
        </Link>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="flex flex-col items-center py-20 text-center">
        <p className="font-display text-xl text-ink">{loadError.title}</p>
        <p className="mt-1.5 max-w-sm text-sm text-ink-muted">{loadError.description}</p>
        <div className="mt-5 flex gap-2">
          <Button variant="secondary" onClick={() => setRetryKey((k) => k + 1)}>
            Try again
          </Button>
          <Link
            href="/contacts"
            className="flex items-center rounded-tab px-4 py-2 text-sm text-ink-muted hover:text-ink"
          >
            Back to all contacts
          </Link>
        </div>
      </div>
    );
  }

  if (!contact) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="skeleton h-8 w-48 animate-shimmer rounded" />
        <div className="skeleton h-40 w-full animate-shimmer rounded-card" />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8">
      <button
        onClick={() => router.back()}
        className="flex w-fit items-center gap-1.5 text-sm text-ink-muted hover:text-ink"
      >
        <ArrowLeft size={15} /> Back
      </button>

      <div className="rounded-card border border-hairline bg-surface p-6 shadow-card sm:p-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-signal-soft font-display text-lg font-medium text-signal-strong">
              {initials(contact.full_name)}
            </div>
            <div>
              <h1 className="font-display text-2xl font-medium text-ink">{contact.full_name}</h1>
              {contact.headline && <p className="mt-0.5 text-ink-muted">{contact.headline}</p>}
              <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm text-ink-muted">
                {contact.current_company && (
                  <span className="flex items-center gap-1.5">
                    <Building2 size={14} className="text-ink-faint" />
                    {contact.current_title ? `${contact.current_title} at ` : ""}
                    {contact.current_company}
                  </span>
                )}
                {contact.location && (
                  <span className="flex items-center gap-1.5">
                    <MapPin size={14} className="text-ink-faint" />
                    {contact.location}
                  </span>
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {contact.linkedin_url && (
              <a
                href={contact.linkedin_url}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1.5 rounded-tab border border-hairline px-3 py-1.5 text-xs text-ink-muted hover:text-ink"
              >
                <ExternalLink size={12} /> LinkedIn
              </a>
            )}
            <Button variant="ghost" size="sm" onClick={handleDelete}>
              <Trash2 size={14} className="text-danger" />
            </Button>
          </div>
        </div>

        {contact.relevance_summary && (
          <div className="mt-6 rounded-card border border-dashed border-tab/40 bg-tab-soft p-4">
            <p className="text-xs font-medium uppercase tracking-wide text-tab">Why they matter</p>
            <p className="mt-1.5 text-sm leading-relaxed text-ink">{contact.relevance_summary}</p>
          </div>
        )}

        {contact.relevance_tags.length > 0 && (
          <div className="mt-4">
            <TagGroup title="Relevance tags" tags={contact.relevance_tags} variant="signal" />
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <div className="flex flex-col gap-8 lg:col-span-2">
          {contact.summary && (
            <section>
              <h2 className="font-display text-lg font-medium text-ink">Summary</h2>
              <p className="mt-2 text-sm leading-relaxed text-ink-muted">{contact.summary}</p>
            </section>
          )}

          {contact.experience.length > 0 && (
            <section>
              <h2 className="mb-4 font-display text-lg font-medium text-ink">Experience</h2>
              <ExperienceTimeline items={contact.experience} />
            </section>
          )}

          {contact.education.length > 0 && (
            <section>
              <h2 className="mb-3 flex items-center gap-2 font-display text-lg font-medium text-ink">
                <GraduationCap size={17} className="text-ink-faint" /> Education
              </h2>
              <EducationList items={contact.education} />
            </section>
          )}

          <section>
            <ConnectionNotes notes={contact.connection_notes} onAdd={handleAddNote} />
          </section>
        </div>

        <div className="flex flex-col gap-5">
          <TagGroup title="Skills" tags={contact.skills} />
          <TagGroup title="Technologies" tags={contact.technologies} />
          <TagGroup title="Domains" tags={contact.domains} />
          <TagGroup title="Capabilities" tags={contact.capabilities} />
          <TagGroup title="Interests" tags={contact.interests} />
        </div>
      </div>
    </div>
  );
}
