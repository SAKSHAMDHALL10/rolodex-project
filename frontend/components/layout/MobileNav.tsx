"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutGrid, Search, UserPlus, Contact2 } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: LayoutGrid },
  { href: "/search", label: "Search", icon: Search },
  { href: "/contacts", label: "Contacts", icon: Contact2 },
  { href: "/ingest", label: "Add", icon: UserPlus },
];

export function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed inset-x-0 bottom-0 z-40 flex justify-around border-t border-hairline bg-surface/95 py-2 backdrop-blur md:hidden">
      {NAV_ITEMS.map((item) => {
        const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex flex-col items-center gap-1 px-3 py-1 text-[11px]",
              active ? "text-signal" : "text-ink-muted"
            )}
          >
            <Icon size={19} strokeWidth={2} />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
