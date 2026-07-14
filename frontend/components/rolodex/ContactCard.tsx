"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Building2, MapPin } from "lucide-react";
import type { ContactListItem } from "@/types";
import { initials } from "@/lib/utils";

export function ContactCard({
  contact,
  index = 0,
  matchedTag,
}: {
  contact: ContactListItem;
  index?: number;
  matchedTag?: string;
}) {
  const topTag = matchedTag ?? contact.relevance_tags[0];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: Math.min(index * 0.04, 0.3), ease: [0.16, 1, 0.3, 1] }}
      className="group relative pt-3"
    >
      {/* Index tab: the card-catalog signature element */}
      <div
        className="absolute left-5 top-0 z-10 flex h-6 w-9 items-center justify-center bg-tab font-mono text-[11px] font-semibold text-canvas"
        style={{ clipPath: "polygon(12% 0, 88% 0, 100% 100%, 0% 100%)" }}
      >
        {initials(contact.full_name).slice(0, 1)}
      </div>

      <Link
        href={`/contacts/${contact.id}`}
        className="block rounded-card border border-hairline bg-surface p-5 pt-6 shadow-card transition-all duration-200 hover:-translate-y-0.5 hover:border-signal/40 hover:shadow-card-hover"
      >
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <h3 className="truncate font-display text-base font-medium text-ink">
              {contact.full_name}
            </h3>
            {contact.headline && (
              <p className="mt-0.5 line-clamp-1 text-sm text-ink-muted">{contact.headline}</p>
            )}
          </div>
        </div>

        <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-ink-muted">
          {contact.current_company && (
            <span className="flex items-center gap-1">
              <Building2 size={12} className="text-ink-faint" />
              {contact.current_company}
            </span>
          )}
          {contact.location && (
            <span className="flex items-center gap-1">
              <MapPin size={12} className="text-ink-faint" />
              {contact.location}
            </span>
          )}
        </div>

        {topTag && (
          <div className="mt-4 border-t border-dashed border-hairline pt-3">
            <span className="relative inline-block text-sm text-ink">
              <span className="absolute inset-x-0 bottom-0.5 h-2 -rotate-[0.4deg] bg-tab-soft" />
              <span className="relative font-medium">{topTag}</span>
            </span>
          </div>
        )}

        {contact.relevance_tags.length > 1 && (
          <div className="mt-2 flex flex-wrap gap-1.5">
            {contact.relevance_tags.slice(1, 4).map((tag) => (
              <span
                key={tag}
                className="rounded-tab border border-hairline px-2 py-0.5 font-mono text-[10.5px] text-ink-muted"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </Link>
    </motion.div>
  );
}
