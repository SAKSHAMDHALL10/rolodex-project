"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutGrid, Search, UserPlus, Contact2, Moon, Sun } from "lucide-react";
import { cn } from "@/lib/utils";
import { useTheme } from "@/hooks/useTheme";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: LayoutGrid },
  { href: "/search", label: "Search", icon: Search },
  { href: "/contacts", label: "All contacts", icon: Contact2 },
  { href: "/ingest", label: "Add contact", icon: UserPlus },
];

export function Sidebar() {
  const pathname = usePathname();
  const { theme, toggle } = useTheme();

  return (
    <aside className="hidden md:flex md:w-60 md:flex-col md:border-r md:border-hairline md:bg-surface/60 md:px-4 md:py-6">
      <Link href="/" className="mb-8 flex items-center gap-2 px-2">
        <span className="flex h-8 w-8 items-center justify-center rounded-tab bg-signal font-mono text-sm font-semibold text-white">
          R
        </span>
        <span className="font-display text-lg font-medium tracking-tight text-ink">
          Rolodex
        </span>
      </Link>

      <nav className="flex flex-1 flex-col gap-1">
        {NAV_ITEMS.map((item) => {
          const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center gap-3 rounded-tab px-3 py-2 text-sm transition-colors",
                active
                  ? "bg-signal-soft text-ink"
                  : "text-ink-muted hover:bg-surface-raised hover:text-ink"
              )}
            >
              <Icon
                size={17}
                strokeWidth={2}
                className={cn(active ? "text-signal" : "text-ink-faint group-hover:text-ink-muted")}
              />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <button
        onClick={toggle}
        className="flex items-center gap-3 rounded-tab px-3 py-2 text-sm text-ink-muted transition-colors hover:bg-surface-raised hover:text-ink"
        aria-label="Toggle color theme"
      >
        {theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}
        {theme === "dark" ? "Light mode" : "Dark mode"}
      </button>
    </aside>
  );
}
