# راهنمای نشر داشبورد پیشرفته در Streamlit Cloud

این پروژه طوری ساخته شده که تمام دیتای عملیاتی را مستقیماً از شیت‌های پروژه داخل Google Sheet مرکزی بخواند.

## Google Sheet مرکزی

ID:

`1wtRzWbJ5uGdc5pqc9KJnauPuFnVQauL31VE9mX-LJ_U`

شیت‌های منبع اپ:

- CBE
- Public Schools
- ECE
- TLS
- VT
- VT_KII_FGD
- Moraa

اپ از `Dashboard` یا `Dashboard_Data` داده نمی‌گیرد.

## مرحله ۱: GitHub

یک Repository خصوصی بساز و تمام فایل‌های ZIP را داخل آن Upload کن.

فایل واقعی Secrets را هیچ وقت داخل GitHub نگذار.

## مرحله ۲: Google Cloud Service Account

در Google Cloud:

1. یک Project بساز.
2. Google Sheets API را Enable کن.
3. Service Account بساز.
4. JSON Key بساز.
5. ایمیل Service Account را Copy کن.

## مرحله ۳: Share کردن Google Sheet

Google Sheet مرکزی را با ایمیل Service Account به شکل Viewer شریک کن.

نیازی نیست Google Sheet را Public بسازی.

## مرحله ۴: Streamlit Cloud

در Streamlit Community Cloud:

- New app
- Repository را انتخاب کن
- Main file = `app.py`

بعد به:

`App → Settings → Secrets`

برو.

ساختار موجود در:

`.streamlit/secrets.example.toml`

را Copy کن و اطلاعات واقعی Service Account را وارد کن.

## امنیت داشبورد عمومی

چون داشبورد عمومی است:

- نام مستفیدها نمایش داده نمی‌شود.
- شماره تماس نمایش داده نمی‌شود.
- نام Field Staff و QA Staff در Chartهای عمومی pseudonymized است.
- Data Explorer فقط فیلدهای عملیاتی غیرحساس را نشان می‌دهد.
- Credentials در Streamlit Secrets باقی می‌ماند.

## امکانات اصلی

- Executive Dashboard
- Project Filter
- Project Deep Dive
- VT Tool Intelligence
- KII/FGD Integration
- Province Analytics
- Monthly Trend
- QA Status
- Rejection Pareto
- Quality Risk
- Field Staff Performance
- Data Quality Alerts
- Public Data Explorer
- CSV Export
- Responsive Dark UI
- Google Sheets live connection
- 5-minute cache + manual refresh

## نکته مهم

اگر ساختار Columnهای شیت‌های پروژه تغییر کند، فقط mapping داخل `src/data_model.py` نیاز به اصلاح دارد. معماری اپ عمداً modular ساخته شده تا مجبور نشوی هر بار کل app.py را جراحی کنی.
