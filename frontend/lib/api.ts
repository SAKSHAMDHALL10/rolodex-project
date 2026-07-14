import type {
  ContactRead,
  ContactListItem,
  DashboardStats,
  IngestResponse,
  SearchResponse,
} from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
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
