# AutoSite Builder

نظام آلي يبني مواقع إلكترونية عربية للمنشآت المحلية التي لا تمتلك موقعاً، بدءاً من البحث عن المنشأة وحتى نشر موقعها على الإنترنت.

## نظرة عامة

يأخذ النظام (مدينة + فئة) وينفذ الخطوات التالية بالترتيب:

1. البحث في Google Places API (الإصدار v1) عن المنشآت في المدينة والفئة.
2. استبعاد كل منشأة لديها موقع إلكتروني.
3. ترتيب الباقي حسب الأولوية (عدد المراجعات، التقييم، وجود هاتف، وزن الفئة).
4. البحث عن روابط إنستقرام وتيك توك وسناب شات وفيسبوك عبر SerpAPI.
5. إرسال بيانات كل منشأة إلى Gemini 1.5 Flash لتوليد محتوى عربي.
6. بناء ملف بيانات JSON لكل منشأة.
7. حفظ البيانات في قاعدة بيانات PostgreSQL.
8. إضافة صف متابعة لكل منشأة في Google Sheets.

## التقنيات

**Backend:** Python، httpx (async)، pydantic، psycopg2، google-generativeai، google-search-results، gspread، loguru، tenacity.

**Frontend:** Next.js 14.2، React 18.3، TypeScript 5.4، Tailwind CSS 3.4.

## التثبيت

```bash
cd backend
python -m venv venv
source venv/bin/activate   # على Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## إعداد متغيرات البيئة

```bash
cp .env.example .env
```

ثم عبّئ القيم التالية داخل `.env`:

- `GOOGLE_PLACES_API_KEY`
- `GEMINI_API_KEY`
- `SERPAPI_KEY`
- `DATABASE_URL`
- `GOOGLE_SHEETS_CREDS` (مسار ملف creds.json)
- `GOOGLE_SHEETS_NAME` (اسم الشيت)
- `LOG_LEVEL`

## التشغيل

```bash
python main.py "جدة" "مطاعم" 5
```

الوسائط بالترتيب: المدينة، الفئة، عدد المنشآت. القيم الافتراضية: جدة، مطاعم، 10.

## تشغيل الـ Frontend

```bash
cd frontend
npm install
npm run dev
```

كل منشأة تحصل على صفحة على المسار `/s/<place_id>`.

## بنية المشروع

```
autosite-builder/
├── backend/
│   ├── src/
│   │   ├── config.py          # إعدادات البيئة
│   │   ├── models.py          # نماذج Pydantic
│   │   ├── db.py              # PostgreSQL
│   │   ├── discovery.py       # Google Places API
│   │   ├── qualification.py   # الترتيب حسب الأولوية
│   │   ├── enrichment.py      # SerpAPI للتواصل الاجتماعي
│   │   ├── content.py         # Gemini لتوليد المحتوى
│   │   ├── builder.py         # بناء ملفات JSON
│   │   ├── sheets.py          # Google Sheets
│   │   └── utils.py           # دوال مساعدة
│   ├── main.py                # خط الإنتاج الكامل
│   ├── main_test.py           # اختبار بدون مفاتيح API
│   └── requirements.txt
└── frontend/
    ├── pages/
    │   ├── _app.tsx
    │   ├── index.tsx
    │   └── s/[slug].tsx
    ├── components/            # Hero, Services, About, Contact, Footer, WhatsAppButton
    ├── data/                  # ملفات JSON لكل منشأة
    └── styles/globals.css
```

## الحصول على المفاتيح

- **Google Places API:** من Google Cloud Console → APIs & Services → Enable APIs → Places API (New)، مع تفعيل الفاتورة (يوجد رصيد مجاني).
- **Gemini API Key:** من aistudio.google.com → Get API Key.
- **SerpAPI Key:** من serpapi.com → Sign Up → Dashboard → API Key.
- **creds.json:** من Google Cloud Console → IAM & Admin → Service Accounts → Create Service Account → Keys → Add Key → Create New Key → JSON.

## النشر

يتم النشر تلقائياً عبر GitHub + Vercel. ملفات `frontend/data/*.json` تُرفع إلى GitHub حتى يبنيها Vercel، لذلك لا تُضاف إلى `.gitignore`.
