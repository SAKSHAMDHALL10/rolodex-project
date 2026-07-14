"use client";

import { createPortal } from "react-dom";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, X } from "lucide-react";
import type { DuplicateCandidate } from "@/types";
import { Button } from "@/components/ui/Button";

export function DuplicateModal({
  duplicates,
  onMerge,
  onCreateAnyway,
  onClose,
}: {
  duplicates: DuplicateCandidate[];
  onMerge: (contactId: string) => Promise<void>;
  onCreateAnyway: () => Promise<void>;
  onClose: () => void;
}) {
  const [mounted, setMounted] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => setMounted(true), []);
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  if (!mounted) return null;

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.97, y: 8 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.2 }}
        className="w-full max-w-lg rounded-card border border-hairline bg-surface p-6 shadow-card-hover"
        role="dialog"
        aria-modal="true"
        aria-label="Possible duplicate contact"
      >
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-tab-soft">
              <AlertTriangle size={16} className="text-tab" />
            </div>
            <h2 className="font-display text-lg font-medium text-ink">Possible duplicate</h2>
          </div>
          <button onClick={onClose} className="text-ink-faint hover:text-ink" aria-label="Close">
            <X size={18} />
          </button>
        </div>

        <p className="mt-3 text-sm text-ink-muted">
          This profile looks like it might already be in your rolodex. Merge into an existing
          entry, or create it as a new contact anyway.
        </p>

        <ul className="mt-4 flex flex-col gap-2.5">
          {duplicates.map((dup) => (
            <li
              key={dup.contact.id}
              className="rounded-card border border-hairline bg-surface-raised p-3.5"
            >
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-ink">{dup.contact.full_name}</p>
                <span className="font-mono text-xs text-ink-faint">
                  {Math.round(dup.similarity_score * 100)}% match
                </span>
              </div>
              <p className="mt-0.5 text-xs text-ink-muted">
                {dup.contact.current_title}
                {dup.contact.current_company ? ` · ${dup.contact.current_company}` : ""}
              </p>
              <p className="mt-1.5 text-[11px] text-ink-faint">{dup.match_reasons.join(" · ")}</p>
              <Button
                size="sm"
                variant="secondary"
                className="mt-2.5 w-full"
                disabled={busy}
                onClick={async () => {
                  setBusy(true);
                  await onMerge(dup.contact.id);
                  setBusy(false);
                }}
              >
                Merge into this contact
              </Button>
            </li>
          ))}
        </ul>

        <div className="mt-5 flex justify-end gap-2">
          <Button variant="ghost" onClick={onClose} disabled={busy}>
            Cancel
          </Button>
          <Button
            variant="secondary"
            disabled={busy}
            onClick={async () => {
              setBusy(true);
              await onCreateAnyway();
              setBusy(false);
            }}
          >
            Create as new contact anyway
          </Button>
        </div>
      </motion.div>
    </div>,
    document.body
  );
}
