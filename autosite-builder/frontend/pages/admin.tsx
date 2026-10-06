import Head from "next/head";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  api,
  API_URL,
  type Health,
  type Job,
  type JobDetail,
  type Lead,
  type LogEntry,
} from "../lib/api";

const CATEGORIES = [
  "مطاعم",
  "مقاهي",
  "عيادات",
  "صيدليات",
  "صالونات",
  "ورش سيارات",
  "محلات ملابس",
  "حلاقين",
  "مخابز",
  "مقاولات",
];

const STATUS_LABELS: Record<string, string> = {
  pending: "بالانتظار",
  running: "قيد التنفيذ",
  done: "مكتملة",
  failed: "فاشلة",
};

const STATUS_STYLES: Record<string, string> = {
  pending: "bg-gray-100 text-gray-600",
  running: "bg-blue-100 text-blue-700 animate-pulse",
  done: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
};

const EVENT_LABELS: Record<string, string> = {
  discovering: "جاري البحث عن المنشآت",
  ranked: "تم ترتيب النتائج",
  building: "جاري بناء موقع",
  built: "تم بناء موقع",
  failed: "فشل بناء موقع",
  done: "اكتمل البناء",
};

function eventText(log: LogEntry): string {
  const d = log.data || {};
  switch (log.event) {
    case "discovering":
      return `البحث عن "${d.category}" في "${d.city}"`;
    case "ranked":
      return `وُجد ${d.found} منشأة، بلا موقع ${d.without_website}، تم اختيار ${d.selected}`;
    case "building":
      return `جاري المعالجة: ${d.name}`;
    case "built":
      return `تم بناء: ${d.name} → ${d.site_url}`;
    case "failed":
      return `فشل: ${d.name} (${d.error})`;
    case "done":
      return `اكتمل البناء: ${d.built} موقع`;
    default:
      return log.event;
  }
}

function eventColor(event: string): string {
  if (event === "built" || event === "done") return "text-green-700";
  if (event === "failed") return "text-red-700";
  if (event === "building") return "text-blue-700";
  return "text-gray-600";
}

function KeyBadge({ label, ok }: { label: string; ok: boolean }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-bold ${
        ok ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
      }`}
    >
      <span className={`h-2 w-2 rounded-full ${ok ? "bg-green-500" : "bg-red-500"}`} />
      {label}: {ok ? "مضبوط" : "مفقود"}
    </span>
  );
}

export default function Admin() {
  const [health, setHealth] = useState<Health | null>(null);
  const [online, setOnline] = useState<boolean | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selected, setSelected] = useState<JobDetail | null>(null);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [form, setForm] = useState({
    city: "جدة",
    category: "مطاعم",
    country: "السعودية",
    limit: 5,
  });
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const activeId = useRef<string | null>(null);

  const loadHealth = useCallback(async () => {
    try {
      const h = await api.health();
      setHealth(h);
      setOnline(true);
    } catch {
      setOnline(false);
      setHealth(null);
    }
  }, []);

  const loadJobs = useCallback(async () => {
    try {
      const list = await api.listJobs();
      setJobs(list);
      const target = activeId.current || list[0]?.id;
      if (target) {
        const detail = await api.getJob(target);
        setSelected(detail);
        if (detail.status === "running" || detail.status === "pending") {
          activeId.current = detail.id;
        } else {
          activeId.current = null;
        }
      }
    } catch {
      /* الخدمة قد تكون متوقفة */
    }
  }, []);

  const loadLeads = useCallback(async () => {
    try {
      const data = await api.listLeads();
      setLeads(data.items);
    } catch {
      /* تجاهل */
    }
  }, []);

  const refresh = useCallback(async () => {
    await Promise.all([loadHealth(), loadJobs()]);
  }, [loadHealth, loadJobs]);

  useEffect(() => {
    refresh();
    loadLeads();
    const timer = setInterval(refresh, 2000);
    return () => clearInterval(timer);
  }, [refresh, loadLeads]);

  async function startBuild(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const job = await api.createJob(form);
      activeId.current = job.id;
      await loadJobs();
    } catch (err) {
      setError(err instanceof Error ? err.message : "تعذّر بدء المهمة");
    } finally {
      setSubmitting(false);
    }
  }

  const busy = health?.busy || submitting;
  const progress =
    selected && selected.selected > 0
      ? Math.min(100, Math.round((selected.built / selected.selected) * 100))
      : 0;

  return (
    <>
      <Head>
        <title>لوحة التحكم — AutoSite Builder</title>
        <meta name="robots" content="noindex" />
      </Head>
      <main dir="rtl" className="font-arabic min-h-screen bg-gray-100 text-gray-900">
        <header className="bg-gradient-to-l from-primary to-blue-900 text-white px-6 py-6">
          <div className="max-w-6xl mx-auto flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl font-extrabold">لوحة التحكم</h1>
              <p className="text-sm text-blue-100 mt-1">
                ابحث عن المنشآت وولّد لها مواقع جاهزة — من الواجهة مباشرة.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span
                className={`rounded-full px-3 py-1 text-xs font-bold ${
                  online
                    ? "bg-green-500/20 text-green-100"
                    : online === false
                      ? "bg-red-500/20 text-red-100"
                      : "bg-white/20 text-white"
                }`}
              >
                {online ? "الخدمة متصلة" : online === false ? "الخدمة متوقفة" : "جاري الفحص…"}
              </span>
            </div>
          </div>
        </header>

        <div className="max-w-6xl mx-auto px-6 py-8 space-y-8">
          {online === false && (
            <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-red-800">
              تعذّر الاتصال بالـ API على <code dir="ltr">{API_URL}</code>. شغّل الخادم
              بالأمر <code dir="ltr">python api.py</code> أو عيّن{" "}
              <code dir="ltr">NEXT_PUBLIC_API_URL</code>.
            </div>
          )}

          {health && (
            <div className="flex flex-wrap gap-2">
              <KeyBadge label="Google Places" ok={health.keys.google_places} />
              <KeyBadge label="Gemini" ok={health.keys.gemini} />
              <KeyBadge label="SerpAPI" ok={health.keys.serpapi} />
            </div>
          )}

          {/* نموذج بدء البناء */}
          <section className="bg-white rounded-2xl shadow-sm p-6">
            <h2 className="text-xl font-bold mb-4">ابدأ مهمة بناء جديدة</h2>
            <form onSubmit={startBuild} className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <label className="flex flex-col gap-1">
                <span className="text-sm font-bold text-gray-600">المدينة</span>
                <input
                  required
                  value={form.city}
                  onChange={(e) => setForm({ ...form, city: e.target.value })}
                  className="rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </label>
              <label className="flex flex-col gap-1">
                <span className="text-sm font-bold text-gray-600">الفئة</span>
                <input
                  required
                  list="categories"
                  value={form.category}
                  onChange={(e) => setForm({ ...form, category: e.target.value })}
                  className="rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                />
                <datalist id="categories">
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c} />
                  ))}
                </datalist>
              </label>
              <label className="flex flex-col gap-1">
                <span className="text-sm font-bold text-gray-600">الدولة</span>
                <input
                  value={form.country}
                  onChange={(e) => setForm({ ...form, country: e.target.value })}
                  className="rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </label>
              <label className="flex flex-col gap-1">
                <span className="text-sm font-bold text-gray-600">عدد المواقع</span>
                <input
                  type="number"
                  min={1}
                  max={50}
                  value={form.limit}
                  onChange={(e) => setForm({ ...form, limit: Number(e.target.value) })}
                  className="rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </label>
              <div className="flex items-end">
                <button
                  type="submit"
                  disabled={busy}
                  className="w-full rounded-lg bg-primary px-4 py-2 font-bold text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {busy ? "جاري التنفيذ…" : "ابدأ البناء"}
                </button>
              </div>
            </form>
            {error && <p className="mt-3 text-sm font-bold text-red-700">{error}</p>}
          </section>

          {/* المهمة الحالية */}
          {selected && (
            <section className="bg-white rounded-2xl shadow-sm p-6">
              <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                <h2 className="text-xl font-bold">
                  {selected.category} في {selected.city}
                </h2>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-bold ${
                    STATUS_STYLES[selected.status] || "bg-gray-100 text-gray-600"
                  }`}
                >
                  {STATUS_LABELS[selected.status] || selected.status}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-4 text-center">
                <div className="rounded-xl bg-gray-50 p-3">
                  <div className="text-2xl font-extrabold text-primary">{selected.found}</div>
                  <div className="text-xs text-gray-500">منشأة موجودة</div>
                </div>
                <div className="rounded-xl bg-gray-50 p-3">
                  <div className="text-2xl font-extrabold text-primary">{selected.selected}</div>
                  <div className="text-xs text-gray-500">مختارة للبناء</div>
                </div>
                <div className="rounded-xl bg-gray-50 p-3">
                  <div className="text-2xl font-extrabold text-green-600">{selected.built}</div>
                  <div className="text-xs text-gray-500">موقع مبني</div>
                </div>
              </div>

              <div className="h-2 w-full rounded-full bg-gray-200 overflow-hidden mb-4">
                <div
                  className="h-full bg-primary transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>

              {selected.error && (
                <p className="mb-3 text-sm font-bold text-red-700">{selected.error}</p>
              )}

              <div className="max-h-72 overflow-y-auto rounded-xl bg-gray-900 p-4 text-sm">
                {selected.logs.length === 0 && (
                  <p className="text-gray-400">لا توجد سجلّات بعد…</p>
                )}
                {selected.logs.map((log, i) => (
                  <div key={i} className="flex gap-3 py-1">
                    <span dir="ltr" className="text-gray-500 shrink-0">
                      {new Date(log.ts).toLocaleTimeString("ar-SA")}
                    </span>
                    <span className={eventColor(log.event)}>{eventText(log)}</span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* المهام السابقة */}
          <section className="bg-white rounded-2xl shadow-sm p-6">
            <h2 className="text-xl font-bold mb-4">المهام السابقة</h2>
            {jobs.length === 0 ? (
              <p className="text-gray-500">لا توجد مهام بعد.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-right">
                  <thead className="text-gray-500">
                    <tr className="border-b">
                      <th className="py-2">المدينة</th>
                      <th className="py-2">الفئة</th>
                      <th className="py-2">الحالة</th>
                      <th className="py-2">مبني</th>
                      <th className="py-2">التاريخ</th>
                    </tr>
                  </thead>
                  <tbody>
                    {jobs.map((job) => (
                      <tr
                        key={job.id}
                        onClick={() => {
                          activeId.current = job.id;
                          api.getJob(job.id).then(setSelected).catch(() => undefined);
                        }}
                        className="cursor-pointer border-b last:border-0 hover:bg-gray-50"
                      >
                        <td className="py-2 font-bold">{job.city}</td>
                        <td className="py-2">{job.category}</td>
                        <td className="py-2">
                          <span
                            className={`rounded-full px-2 py-0.5 text-xs font-bold ${
                              STATUS_STYLES[job.status] || ""
                            }`}
                          >
                            {STATUS_LABELS[job.status] || job.status}
                          </span>
                        </td>
                        <td className="py-2">{job.built}</td>
                        <td className="py-2 text-gray-500" dir="ltr">
                          {new Date(job.created_at).toLocaleString("ar-SA")}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {/* المنشآت */}
          <section className="bg-white rounded-2xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">المنشآت المخزّنة</h2>
              <button
                onClick={loadLeads}
                className="rounded-lg border border-gray-300 px-3 py-1 text-sm font-bold text-gray-700 hover:bg-gray-50"
              >
                تحديث
              </button>
            </div>
            {leads.length === 0 ? (
              <p className="text-gray-500">لا توجد منشآت مخزّنة بعد.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-right">
                  <thead className="text-gray-500">
                    <tr className="border-b">
                      <th className="py-2">الاسم</th>
                      <th className="py-2">الفئة</th>
                      <th className="py-2">المدينة</th>
                      <th className="py-2">الهاتف</th>
                      <th className="py-2">التقييم</th>
                      <th className="py-2">المراجعات</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leads.map((lead) => (
                      <tr key={lead.place_id} className="border-b last:border-0">
                        <td className="py-2 font-bold">{lead.name}</td>
                        <td className="py-2">{lead.category}</td>
                        <td className="py-2">{lead.city}</td>
                        <td className="py-2" dir="ltr">
                          {lead.phone || "—"}
                        </td>
                        <td className="py-2">{lead.rating ?? "—"}</td>
                        <td className="py-2">{lead.reviews_count ?? "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </div>
      </main>
    </>
  );
}
