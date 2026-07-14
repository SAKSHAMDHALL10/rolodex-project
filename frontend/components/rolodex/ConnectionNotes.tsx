"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import type { ConnectionNote, ConnectionNoteType } from "@/types";
import { formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { Textarea } from "@/components/ui/Input";

const NOTE_TYPE_LABELS: Record<ConnectionNoteType, string> = {
  met_at_hackathon: "Met at hackathon",
  worked_together: "Worked together",
  referral: "Referral",
  investor: "Investor",
  mentor: "Mentor",
  mutual_connection: "Mutual connection",
  future_collaboration: "Future collaboration",
  other: "Note",
};

const NOTE_TYPES = Object.keys(NOTE_TYPE_LABELS) as ConnectionNoteType[];

export function ConnectionNotes({
  notes,
  onAdd,
}: {
  notes: ConnectionNote[];
  onAdd: (note: { note_type: ConnectionNoteType; text: string }) => Promise<void>;
}) {
  const [adding, setAdding] = useState(false);
  const [noteType, setNoteType] = useState<ConnectionNoteType>("worked_together");
  const [text, setText] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit() {
    if (!text.trim()) return;
    setSaving(true);
    try {
      await onAdd({ note_type: noteType, text: text.trim() });
      setText("");
      setAdding(false);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <h3 className="font-display text-sm font-medium text-ink">Connection notes</h3>
        {!adding && (
          <button
            onClick={() => setAdding(true)}
            className="flex items-center gap-1 text-xs text-signal hover:underline"
          >
            <Plus size={13} /> Add note
          </button>
        )}
      </div>

      {adding && (
        <div className="mt-3 rounded-card border border-hairline bg-surface-raised p-3">
          <div className="mb-2 flex flex-wrap gap-1.5">
            {NOTE_TYPES.map((type) => (
              <button
                key={type}
                onClick={() => setNoteType(type)}
                className={`rounded-tab px-2 py-1 font-mono text-[10.5px] transition-colors ${
                  noteType === type
                    ? "bg-signal text-white"
                    : "border border-hairline text-ink-muted hover:text-ink"
                }`}
              >
                {NOTE_TYPE_LABELS[type]}
              </button>
            ))}
          </div>
          <Textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="How do you know them, or what should you remember?"
            rows={2}
          />
          <div className="mt-2 flex justify-end gap-2">
            <Button variant="ghost" size="sm" onClick={() => setAdding(false)}>
              Cancel
            </Button>
            <Button size="sm" onClick={submit} disabled={saving || !text.trim()}>
              {saving ? "Saving…" : "Save note"}
            </Button>
          </div>
        </div>
      )}

      {notes.length === 0 && !adding ? (
        <p className="mt-2 text-sm text-ink-faint">No notes yet — add context on how you know them.</p>
      ) : (
        <ul className="mt-3 flex flex-col gap-2.5">
          {notes.map((note, i) => (
            <li key={i} className="rounded-card border border-hairline bg-surface p-3">
              <div className="flex items-center justify-between">
                <span className="rounded-tab bg-tab-soft px-2 py-0.5 font-mono text-[10.5px] text-tab">
                  {NOTE_TYPE_LABELS[note.note_type]}
                </span>
                <span className="text-[11px] text-ink-faint">{formatDate(note.created_at)}</span>
              </div>
              <p className="mt-1.5 text-sm text-ink-muted">{note.text}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
