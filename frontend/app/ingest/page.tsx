"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Sparkles, ClipboardPaste } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import type { DuplicateCandidate } from "@/types";
import { Button } from "@/components/ui/Button";
import { Input, Textarea } from "@/components/ui/Input";
import { DuplicateModal } from "@/components/rolodex/DuplicateModal";
import { useToast } from "@/hooks/useToast";

const SAMPLE_PROFILE = `Priya Shenoy
Senior Backend Engineer @ Finlynk | Ex-Razorpay | Distributed Payments Systems
Bengaluru, Karnataka, India

About
I build the boring, unglamorous infrastructure that makes payments actually
work at 2am on a Sunday. Nine years writing backend systems for companies
that move real money, most recently leading the ledger-reconciliation
rewrite at Finlynk that cut settlement mismatches by 94%.

Experience
Senior Backend Engineer — Finlynk (Jan 2022 - Present)
Backend Engineer — Razorpay (Jun 2018 - Dec 2021)

Education
National Institute of Technology Karnataka (NITK), Surathkal — B.Tech, CS

Skills: Distributed Systems, Kafka, PostgreSQL, Payments Infrastructure, Go, Python`;

export default function IngestPage() {
  const router = useRouter();
  const { push } = useToast();
  const [rawText, setRawText] = useState("");
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [duplicates, setDuplicates] = useState<DuplicateCandidate[] | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!rawText.trim()) {
      push("Paste the profile text first.", "error");
      return;
    }
    setLoading(true);
    try {
      const res = await api.contacts.ingest({
        source_type: "text",
        raw_text: rawText,
        linkedin_url: linkedinUrl || undefined,
      });
      if (res.status === "possible_duplicate") {
        setDuplicates(res.duplicates);
      } else if (res.contact) {
        push(`${res.contact.full_name} added to your rolodex.`, "success");
        router.push(`/contacts/${res.contact.id}`);
      }
    } catch (err) {
      push(
        err instanceof ApiError
          ? err.message
          : "Couldn't reach the Rolodex API. Is the backend running?",
        "error"
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateAnyway() {
    setLoading(true);
    try {
      const res = await api.contacts.ingestForce({
        source_type: "text",
        raw_text: rawText,
        linkedin_url: linkedinUrl || undefined,
      });
      if (res.contact) {
        push(`${res.contact.full_name} added to your rolodex.`, "success");
        router.push(`/contacts/${res.contact.id}`);
      }
    } catch {
      push("Couldn't create the contact.", "error");
    } finally {
      setLoading(false);
      setDuplicates(null);
    }
  }

  async function handleMerge(existingId: string) {
    setLoading(true);
    try {
      const created = await api.contacts.ingestForce({
        source_type: "text",
        raw_text: rawText,
        linkedin_url: linkedinUrl || undefined,
      });
      if (!created.contact) throw new Error("Extraction failed");
      const merged = await api.contacts.merge(existingId, created.contact.id);
      push(`Merged into ${merged.full_name}.`, "success");
      router.push(`/contacts/${merged.id}`);
    } catch {
      push("Couldn't merge automatically — opening the existing contact instead.", "error");
      router.push(`/contacts/${existingId}`);
    } finally {
      setLoading(false);
      setDuplicates(null);
    }
  }

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <div>
        <h1 className="font-display text-2xl font-medium text-ink">Add a contact</h1>
        <p className="mt-1 text-ink-muted">
          Paste a LinkedIn profile (page text or export). The extraction pipeline pulls out
          identity, capabilities, and — most importantly — why this person is worth knowing.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className="mb-1.5 block text-xs font-medium uppercase tracking-wide text-ink-faint">
            LinkedIn URL <span className="normal-case text-ink-faint">(optional, for reference)</span>
          </label>
          <Input
            value={linkedinUrl}
            onChange={(e) => setLinkedinUrl(e.target.value)}
            placeholder="https://www.linkedin.com/in/..."
          />
        </div>

        <div>
          <div className="mb-1.5 flex items-center justify-between">
            <label className="text-xs font-medium uppercase tracking-wide text-ink-faint">
              Profile text
            </label>
            <button
              type="button"
              onClick={() => setRawText(SAMPLE_PROFILE)}
              className="flex items-center gap-1 text-xs text-signal hover:underline"
            >
              <ClipboardPaste size={12} /> Use a sample profile
            </button>
          </div>
          <Textarea
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            placeholder="Paste the full LinkedIn profile page text here…"
            rows={14}
            className="font-mono text-[13px] leading-relaxed"
          />
          <p className="mt-1.5 text-xs text-ink-faint">
            Navigation chrome, ads, and duplicate lines are cleaned automatically before extraction.
          </p>
        </div>

        <Button type="submit" size="lg" disabled={loading} className="w-fit">
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
          {loading ? "Extracting…" : "Generate contact"}
        </Button>
      </form>

      {duplicates && (
        <DuplicateModal
          duplicates={duplicates}
          onMerge={handleMerge}
          onCreateAnyway={handleCreateAnyway}
          onClose={() => setDuplicates(null)}
        />
      )}
    </div>
  );
}
