<div dir="rtl">

# 📢 Telegram Ads Manager

سیستم مدیریت تبلیغات تلگرامی، شامل **ربات مشتری** و **ربات دانلودر**، نوشته‌شده با پایتون.

> ⚠️ **این پروژه آرشیو شده و فقط خواندنی است.** دیگر توسعه داده نمی‌شود.

## ✨ قابلیت‌ها

- ⚠️ ربات مشتری برای ثبت و مدیریت سفارش تبلیغات (`run_customer.py`)
- ⚠️ ربات دانلودر برای دریافت و پردازش محتوا (`run_downloader.py`)
- پایگاه داده PostgreSQL با SQLAlchemy
- ⚠️ پرداخت با ارز دیجیتال (TRON / Ethereum)
- ⚠️ کپچا برای تأیید کاربران
- ⚠️ تاریخ شمسی و زمان‌بندی کارها

(موارد ⚠️ را قبل از انتشار بررسی و اصلاح کنید.)

## 🗂️ ساختار پروژه

```
telegram-ads-manager/
├── bot/                  # هسته ربات (CustomerBot)
├── config/               # تنظیمات
├── customer_handlers/    # هندلرهای ربات مشتری
├── downloader_handlers/  # هندلرهای ربات دانلودر
├── database/             # مدل‌ها و CRUD (SQLAlchemy)
├── utils/                # توابع کمکی
├── run_customer.py       # اجرای ربات مشتری
├── run_downloader.py     # اجرای ربات دانلودر
└── requirements.txt
```

## 🧰 تکنولوژی‌ها

- Python
- python-telegram-bot 22.5
- SQLAlchemy 2 + PostgreSQL (psycopg2)
- APScheduler
- aiohttp / httpx
- tronpy / eth-utils
- Pillow, captcha, jdatetime

## 🚀 نصب و اجرا

۱. دریافت پروژه:

```bash
git clone https://github.com/JafariHosein/telegram-ads-manager.git
cd telegram-ads-manager
```

۲. نصب وابستگی‌ها:

```bash
python -m venv venv
source venv/bin/activate        # در ویندوز: venv\Scripts\activate
pip install -r requirements.txt
```

۳. یک پایگاه داده PostgreSQL بسازید و توکن ربات‌ها و اطلاعات دیتابیس را در پوشه `config/` تنظیم کنید. ⚠️ (نام دقیق فایل و متغیرها را اینجا بنویسید.)

۴. اجرا (هر ربات در یک ترمینال جدا):

```bash
python run_customer.py
python run_downloader.py
```

## 📌 وضعیت پروژه

این ریپو برای ثبت سابقه کار و استفاده به‌عنوان نمونه نگه‌داری می‌شود و آرشیو شده است.

</div>
