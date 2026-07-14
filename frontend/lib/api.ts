import type {
  ContactRead,
  ContactListItem,
  DashboardStats,
  IngestResponse,
  SearchResponse,
} from "@/types";

const RAW_API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

/**
 * Validates and normalizes NEXT_PUBLIC_API_URL into an absolute base URL.
 *
 * This MUST be an absolute URL (scheme + host [+ path]), e.g.
 * "https://your-backend.up.railway.app/api/v1". A bare domain or a value
 * missing the scheme (a real, easy-to-make mistake when pasting a Railway/
 * Render host into Vercel's env var settings) is NOT rejected by plain
 * string concatenation - `fetch(`${base}${path}`)` silently treats a
 * scheme-less string as a *relative* URL and resolves it against the
 * current page's origin, producing nonsense like
 * "https://your-app.vercel.app/your-backend.up.railway.app/dashboard"
 * and a confusing 404, with no indication of what actually went wrong.
 *
 * `new URL(raw)` throws immediately on anything that isn't already a fully
 * qualified absolute URL, which is exactly the behavior we want here: fail
 * loudly and specifically the first time the API client is used, never
 * silently construct a URL relative to window.location / the Vercel domain.
 */
function resolveApiBaseUrl(raw: string): string {
  let parsed: URL;
  try {
    parsed = new URL(raw);
  } catch {
    throw new ApiError(
      `NEXT_PUBLIC_API_URL is not a valid absolute URL: ${JSON.stringify(raw)}. ` +
        'It must include the scheme and host, e.g. "https://your-backend.up.railway.app/api/v1". ' +
        "Check the environment variable in your Vercel project settings (Production scope) - " +
        "do not use a bare domain.",
      0
    );
  }
  // Normalize away a trailing slash so `${base}${path}` (path always starts
  // with "/") never produces a double slash.
  return parsed.toString().replace(/\/$/, "");
}

let cachedApiUrl: string | null = null;

function getApiUrl(): string {
  if (cachedApiUrl === null) {
    cachedApiUrl = resolveApiBaseUrl(RAW_API_URL);
  }
  return cachedApiUrl;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${getApiUrl()}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
      /* response wasn't JSON */
    }
    throw new ApiError(detail || "Request failed", res.status);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  dashboard: () => request<DashboardStats>("/dashboard"),

  contacts: {
    list: (params?: { limit?: number; offset?: number }) => {
      const qs = new URLSearchParams();
      if (params?.limit) qs.set("limit", String(params.limit));
      if (params?.offset) qs.set("offset", String(params.offset));
      const suffix = qs.toString() ? `?${qs.toString()}` : "";
      return request<ContactListItem[]>(`/contacts${suffix}`);
    },
    get: (id: string) => request<ContactRead>(`/contacts/${id}`),
    ingest: (payload: {
      source_type: "text" | "url" | "export";
      raw_text?: string;
      linkedin_url?: string;
    }) =>
      request<IngestResponse>("/contacts/ingest", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    ingestForce: (payload: {
      source_type: "text" | "url" | "export";
      raw_text?: string;
      linkedin_url?: string;
    }) =>
      request<IngestResponse>("/contacts/ingest/force", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    update: (
      id: string,
      payload: Partial<{
        connection_notes: { note_type: string; text: string; created_at: string }[];
        relevance_summary: string;
        relevance_tags: string[];
      }>
    ) =>
      request<ContactRead>(`/contacts/${id}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      }),
    remove: (id: string) => request<void>(`/contacts/${id}`, { method: "DELETE" }),
    merge: (keepId: string, duplicateId: string) =>
      request<ContactRead>("/contacts/merge", {
        method: "POST",
        body: JSON.stringify({ keep_id: keepId, duplicate_id: duplicateId }),
      }),
  },

  search: {
    naturalLanguage: (query: string) =>
      request<SearchResponse>("/search/natural-language", {
        method: "POST",
        body: JSON.stringify({ query }),
      }),
    structured: (payload: {
      query?: string;
      filters?: Record<string, unknown>;
      semantic?: boolean;
      limit?: number;
    }) =>
      request<SearchResponse>("/search", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
  },
};
