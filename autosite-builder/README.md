# AutoSite Builder

نظام آلي يبني مواقع إلكترونية عربية للمنشآت المحلية التي لا تمتلك موقعاً، بدءاً من البحث عن المنشأة وحتى نشر موقعها على الإنترنت.

## نظرة عامة

يأخذ النظام (مدينة + فئة) وينفذ الخطوات التالية بالترتيب:

1. البحث في Google Places API (الإصدار v1) عن المنشآت في المدينة والفئة.
2. استبعاد كل منشأة لديها موقع إلكتروني.
3. ترتيب الباقي حسب الأولوية (عدد المراجعات، التقييم، وجود هاتف، وزن الفئة).
4. البحث عن روابط إنستقرام وتيك توك وسناب شات وفيسبوك عبر SerpAPI.
5. إرسال بيانات كل منشأة إلى Gemini 2.0 Flash لتوليد محتوى عربي.
6. بناء ملف بيانات JSON لكل منشأة.
7. حفظ البيانات في قاعدة بيانات PostgreSQL.
8. إضافة صف متابعة لكل منشأة في Google Sheets.
9. (اختياري) نشر ملفات JSON إلى GitHub ليُعيد Vercel بناء المواقع تلقائياً.

## التقنيات

**Backend:** Python 3.11+، httpx (async)، pydantic v2، psycopg2، google-genai، google-search-results، gspread، loguru، tenacity.

**Frontend:** Next.js 14.2 (آخر إصدار مصحّح أمنياً)، React 18.3، TypeScript 5.4، Tailwind CSS 3.4.

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

### 1) عبر لوحة التحكم (واجهات الويب) — الطريقة الموصى بها

شغّل الـ API ثم الواجهة:

```bash
# نافذة أولى: قاعدة البيانات
docker compose up -d db

# نافذة ثانية: واجهة برمجية + لوحة التحكم
cd backend
python api.py            # يعمل على http://localhost:8000

# نافذة ثالثة: الواجهة الأمامية
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

ثم افتح `http://localhost:3000/admin`، واختر المدينة والفئة وعدد المواقع، واضغط
«ابدأ البناء» — ستتابع التقدّم والسجلّات مباشرة، وترى المهام السابقة والمنشآت المخزّنة.

أو شغّل الـ API ضمن Docker مع قاعدة البيانات:

```bash
docker compose up -d        # يشغّل db + api معاً
```

### 2) عبر سطر الأوامر

```bash
python main.py "جدة" "مطاعم" 5
```

الوسائط بالترتيب: المدينة، الفئة، عدد المنشآت. القيم الافتراضية: جدة، مطاعم، 10.

## واجهة الـ API

| الطريقة | المسار | الوصف |
|---|---|---|
| GET | `/api/health` | جاهزية الخدمة ووجود المفاتيح |
| GET | `/api/config` | القيم الافتراضية (دون كشف المفاتيح) |
| GET | `/api/jobs` | كل المهام |
| POST | `/api/jobs` | بدء مهمة بناء جديدة `{city, category, country, limit}` |
| GET | `/api/jobs/{id}` | حالة مهمة مع سجلّات التقدّم |
| GET | `/api/leads` | المنشآت المخزّنة في قاعدة البيانات |

التوثيق التفاعلي (Swagger) متاح على `http://localhost:8000/docs`.

لإتاحة الـ API للواجهة على نطاق آخر، اضبط `API_CORS_ORIGINS` (مفصولة بفواصل).

## تشغيل الـ Frontend

```bash
cd frontend
npm install
npm run dev
```

كل منشأة تحصل على صفحة على المسار `/s/<place_id>`، مع خريطة موقع على `/sitemap.xml`.

## قاعدة بيانات محلية (Docker)

لتشغيل PostgreSQL محلياً دون تثبيت:

```bash
docker compose up -d db
```

ثم ضع في `.env`:

```
DATABASE_URL=postgresql://autosite:autosite@localhost:5432/autosite
```

## الاختبار والفحص

```bash
cd backend
pytest -q          # 24 اختباراً لا تحتاج مفاتيح API
ruff check .       # فحص الكود
```

## النشر التلقائي (GitHub + Vercel)

```bash
cd backend
python publish.py "جدة" "مطاعم" 5
```

يبني المواقع ثم يدفع ملفات `frontend/data/*.json` إلى GitHub، فيُعيد Vercel بناء المواقع تلقائياً.

لضبط Vercel: اختر المستودع ثم اجعل **Root Directory** هو `autosite-builder/frontend`.

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
│   │   ├── jobs.py            # إدارة مهام البناء في الخلفية
│   │   ├── sheets.py          # Google Sheets
│   │   └── utils.py           # دوال مساعدة
│   ├── main.py                # خط الإنتاج الكامل
│   ├── api.py                 # واجهة REST + لوحة التحكم
│   ├── main_test.py           # اختبار بدون مفاتيح API
│   └── requirements.txt
└── frontend/
    ├── pages/
    │   ├── _app.tsx
    │   ├── index.tsx
    │   ├── admin.tsx          # لوحة التحكم
    │   └── s/[slug].tsx
    ├── lib/api.ts             # عميل الـ API
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
