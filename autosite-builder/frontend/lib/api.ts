/**
 * عميل بسيط للتواصل مع الـ API الخلفي.
 * عيّن NEXT_PUBLIC_API_URL في ملف .env.local أو في إعدادات Vercel.
 */

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

export interface Health {
  status: string;
  busy: boolean;
  active_job: string | null;
  keys: { google_places: boolean; gemini: boolean; serpapi: boolean };
}

export interface LogEntry {
  ts: string;
  event: string;
  data: Record<string, unknown>;
}

export interface Job {
  id: string;
  city: string;
  category: string;
  country: string;
  limit: number;
  status: "pending" | "running" | "done" | "failed";
  built: number;
  found: number;
  selected: number;
  error: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export interface JobDetail extends Job {
  logs: LogEntry[];
}

export interface Lead {
  place_id: string;
  name: string;
  category: string;
  city: string;
  phone: string | null;
  rating: number | null;
  reviews_count: number | null;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
  });
  if (!response.ok) {
    let detail = `خطأ ${response.status}`;
    try {
      const body = await response.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* تجاهل */
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<Health>("/api/health"),
  listJobs: () => request<Job[]>("/api/jobs"),
  getJob: (id: string) => request<JobDetail>(`/api/jobs/${id}`),
  createJob: (payload: {
    city: string;
    category: string;
    country?: string;
    limit?: number;
  }) =>
    request<Job>("/api/jobs", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  listLeads: () => request<{ count: number; items: Lead[] }>("/api/leads"),
};
