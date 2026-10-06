# AGENTS.md

ذاكرة المشروع للأعمال المستقبلية داخل هذا المستودع.

## نظرة عامة

AutoSite Builder: نظام آلي يأخذ (مدينة + فئة) فيبني مواقع إلكترونية عربية للمنشآت
التي لا تملك موقعاً. الجزء الرئيسي داخل مجلد `autosite-builder/`.

## البنية

- `autosite-builder/backend/` — Python، خط الإنتاج الكامل.
  - `main.py` — نقطة التشغيل: `python main.py "جدة" "مطاعم" 5`
  - `main_test.py` — اختبار بدون مفاتيح API (يكتب JSON تجريبي في `frontend/data`).
  - `src/` — config, models, utils, db, discovery, qualification, enrichment, content, builder, sheets.
- `autosite-builder/frontend/` — Next.js 14 + TypeScript + Tailwind (RTL).
  - صفحة ديناميكية: `pages/s/[slug].tsx` تقرأ `data/<place_id>.json` (ISR 60s, fallback blocking).

## قواعد يجب الالتزام بها

- Places API v1 يرجع `websiteUri` في نتائج البحث مباشرة — لا تستخدم Place Details منفصل.
- استخدم Gemini 1.5 Flash، وليس gemini-pro.
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
python main_test.py                 # اختبار بدون مفاتيح
python main.py "جدة" "مطاعم" 5      # التشغيل الكامل

# frontend
cd autosite-builder/frontend
npm install
npm run build
npm run dev
```

## قيود بيئية معروفة

- إصدارات `requirements.txt` المثبّتة تحتاج Python 3.11/3.12. على Python 3.13
  لا توجد wheels لـ `psycopg2-binary 2.9.9` و`pydantic 2.7.0`؛ استخدم نسخاً أحدث للاختبار فقط.
- `typescript` كان `5.4.0` غير موجود على npm؛ الصحيح `5.4.5`.

## النشر

GitHub + Vercel تلقائياً. لا تكتب كود نشر يدوي. المستودع: `kayansoft1/tools`.
