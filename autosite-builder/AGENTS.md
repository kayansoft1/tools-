# AGENTS.md

ذاكرة المشروع للأعمال المستقبلية داخل هذا المستودع.

## نظرة عامة

AutoSite Builder: نظام آلي يأخذ (مدينة + فئة) فيبني مواقع إلكترونية عربية للمنشآت
التي لا تملك موقعاً. الجزء الرئيسي داخل مجلد `autosite-builder/`.

## البنية

- `autosite-builder/backend/` — Python، خط الإنتاج الكامل.
  - `main.py` — نقطة التشغيل: `python main.py "جدة" "مطاعم" 5` (و`process()` تقبل `progress`).
  - `api.py` — واجهة REST (FastAPI) للتحكم عبر الويب: `python api.py` على المنفذ 8000.
  - `src/jobs.py` — إدارة مهام البناء في الخلفية (مهمة واحدة نشطة، سجلّات، تنظيف).
  - `main_test.py` — اختبار بدون مفاتيح API (يكتب JSON تجريبي في `frontend/data`).
  - `publish.py` — يبني المواقع ثم يدفع ملفات JSON إلى GitHub (لإعادة بناء Vercel).
  - `tests/` — اختبارات pytest لا تحتاج مفاتيح API.
  - `src/` — config, models, utils, db, discovery, qualification, enrichment, content, builder, jobs, sheets.
- `autosite-builder/frontend/` — Next.js 14.2 + TypeScript + Tailwind (RTL).
  - `pages/admin.tsx` — لوحة التحكم (بدء مهمة، متابعة تقدّم حيّة، المهام، المنشآت).
  - `lib/api.ts` — عميل الـ API (يقرأ `NEXT_PUBLIC_API_URL`).
  - صفحة ديناميكية: `pages/s/[slug].tsx` تقرأ `data/<place_id>.json` (ISR 60s, fallback blocking).
  - `pages/sitemap.xml.tsx` — خريطة موقع ديناميكية. `public/robots.txt`.
- `.github/workflows/ci.yml` — CI: backend (ruff + pytest) و frontend (typecheck + build).
- `autosite-builder/docker-compose.yml` — PostgreSQL + API محليان للتطوير.

## قواعد يجب الالتزام بها

- Places API v1 يرجع `websiteUri` في نتائج البحث مباشرة — لا تستخدم Place Details منفصل.
- استخدم Gemini 2.0 Flash عبر SDK `google-genai` (وليس `google-generativeai` القديم).
- استخدم httpx غير المتزامن (async)، وليس googlemaps المتزامنة.
- استخدم psycopg2 مباشرة، وليس supabase.
- الـ slug لكل منشأة هو `place_id`، وليس الاسم العربي.
- أسماء المتغيرات والدوال بالإنجليزية، والتعليقات بالعربية للأجزاء المهمة فقط.
- `frontend/data/*.json` يجب أن تُرفع إلى GitHub (لا تُضاف إلى `.gitignore`) حتى يبنيها Vercel.

## أوامر مهمة

```bash
# backend
cd autosite-builder/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m pytest -q                  # اختبارات الوحدة
ruff check .                         # فحص الكود
python main_test.py                  # اختبار بدون مفاتيح
python main.py "جدة" "مطاعم" 5       # التشغيل الكامل
python api.py                        # واجهة التحكم عبر الويب
python publish.py "جدة" "مطاعم" 5    # بناء + نشر إلى GitHub

# frontend
cd autosite-builder/frontend
npm ci
npm run typecheck
npm run build
npm run dev

# قاعدة بيانات محلية
docker compose up -d db
```

## قيود بيئية معروفة

- الإصدارات في `requirements.txt` تعمل على Python 3.11/3.12/3.13 (لا توجد مشكلة wheels الآن).

## النشر

GitHub + Vercel تلقائياً. لا تكتب كود نشر يدوي. المستودع: `kayansoft1/tools-`.
