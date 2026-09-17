# راهنمای نشر نسخه Ultra-Modern در Streamlit Cloud

این نسخه مستقیماً از شیت‌های پروژه داخل Google Sheet مرکزی استفاده می‌کند و برای داشبورد عمومی طراحی شده است.

## شیت‌های منبع

- CBE
- Public Schools
- ECE
- TLS
- VT
- VT_KII_FGD
- Moraa

داشبورد Streamlit از `Dashboard` و `Dashboard_Data` برای محاسبات استفاده نمی‌کند.

## مراحل نشر

1. محتویات پروژه را در یک GitHub Repository خصوصی قرار بده.
2. در Google Cloud، `Google Sheets API` را فعال کن.
3. یک Service Account بساز و JSON Key بگیر.
4. Google Sheet مرکزی را با ایمیل Service Account به شکل Viewer شریک کن.
5. در Streamlit Cloud به `Settings → Secrets` برو.
6. محتوای `.streamlit/secrets.example.toml` را با مقادیر واقعی Service Account پر کن.
7. Main file را `app.py` انتخاب کن.
8. Deploy کن و یک‌بار App را Reboot کن.

## Dark-only

نسخه Streamlit روی `1.63.0` قفل شده، Light و Dark هر دو با Dark palette تعریف شده‌اند، Toolbar محدود شده و CSS dark lock نیز فعال است.

## امنیت

- Private Key را در GitHub قرار نده.
- فایل واقعی `secrets.toml` را Commit نکن.
- نام و شماره تماس مستفیدها در Data Explorer عمومی نمایش داده نمی‌شود.
- Field Staff و QA Reviewer در تحلیل عمومی pseudonymized هستند.
