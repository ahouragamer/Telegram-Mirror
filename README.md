<div align="center">

<img src="https://img.shields.io/badge/version-3.0-blue?style=flat-square" alt="version"/>

# 📡 TELEGRAM MIRROR

### خواندن و دانلود محتوی از کانال‌های تلگرام بدون فیلتر، مستقیم از گیتهاب

[![GitHub Actions](https://img.shields.io/badge/Powered%20by-GitHub%20Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![فارسی](https://img.shields.io/badge/زبان-فارسی-dc2626?style=for-the-badge)](README.md)

**بدون VPN · بدون نصب · بدون API Token**

اگه این پروژه برات مفیده، با یه ⭐ حمایت کن!
[![GitHub Repo stars](https://img.shields.io/github/stars/FALKON-CODE/Telegram-Mirror?style=social)](https://github.com/FALKON-CODE/Telegram-Mirror)

</div>

---

## 🧠 چطور کار می‌کنه؟

سرورهای GitHub در خارج از ایران هستند و به تلگرام دسترسی دارند. این پروژه از **GitHub Actions** استفاده می‌کنه تا محتوای کانال‌های تلگرام رو از طرف شما دریافت کنه و داخل مخزن ذخیره کنه. بعدش شما مستقیم از `github.com` می‌تونید اون‌ها رو ببینید — بدون VPN.

```
شما  ──►  GitHub Action  ──►  تلگرام  ──►  فایل داخل مخزن  ──►  شما روی github.com
```

---

## ✨ قابلیت‌ها

| ابزار | کاربرد |
|:-----:|:-------|
| 📡 **Channel Reader** | خواندن آخرین پیام‌های یک کانال عمومی |
| ⬇️ **Post Downloader** | دانلود فایل، ویدیو، عکس یا صدا از یک پست مشخص |

- 📨 دریافت تا **۲۰۰ پیام** از هر کانال عمومی
- 🖼 نمایش **عکس و آلبوم** مستقیم داخل صفحه
- ⬇️ دانلود **ویدیو، عکس، اسناد و هر فایلی** از پست‌های تلگرام
- 📦 تقسیم خودکار فایل‌های بالای **۱۰۰MB** به قطعات زیپ
- ⚡ بدون نیاز به هیچ‌گونه توکن یا ربات

---

## 🚀 راه‌اندازی — یک‌بار، ۲ دقیقه

### ۱. Fork کردن مخزن

روی دکمه **Fork** در بالای همین صفحه کلیک کنید تا یه نسخه از این مخزن برای خودتون بسازید.

### ۲. دادن مجوز به Actions

وارد مخزن Fork شده‌تان بشید و برید به:

```
Settings → Actions → General → Workflow permissions
```

گزینه **Read and write permissions** را انتخاب و **Save** کنید.

### ۳. تمام! ↓

---

## 📖 ابزار اول — Channel Reader

با این ابزار می‌تونید آخرین پیام‌های هر کانال عمومی تلگرام رو بخونید.

### نحوه استفاده

به تب **Actions** مخزن خود بروید:

1. روی **📡 Fetch Telegram Channel** کلیک کنید
2. روی **Run workflow** کلیک کنید
3. نام کانال را **بدون @** وارد کنید — مثال: `channel_username`
4. تعداد پیام را وارد کنید (پیش‌فرض: ۱۰۰)
5. **Run workflow** را بزنید

بعد از چند ثانیه، یه فایل Markdown داخل پوشه `channels/` ساخته میشه که می‌تونید مستقیم روی GitHub بخونیدش.

> 💡 **نکته:** خواندن یک پست خاص: اگه فقط می‌خواید یه پست مشخص رو بخونید، کافیه لینک اون پست رو توی فیلد post وارد کنید — مثال: https://t.me/channelname/123. فقط همون پست خوانده و ذخیره میشه.
> 💡 **نکته:** پست‌هایی که ویدیو، صدا یا فایل دارند، یه باکس مخصوص دانلود دارند. لینک پست رو کپی کنید، بعد برید **Actions ← ⬇️ Download Telegram Post** و paste کنید.

---

## ⬇️ ابزار دوم — Post Downloader

با این ابزار می‌تونید **فایل‌های داخل یک پست مشخص** تلگرام رو دانلود کنید — ویدیو، عکس، اسناد، موزیک یا هر فایل دیگه‌ای.

### نحوه استفاده

**مرحله ۱ — لینک پست رو بگیرید**

دو راه دارید:

**راه اول — مستقیم از فایل MD (راحت‌تر):**
داخل فایل کانال، زیر هر ویدیو یا فایل یه باکس اینجوری می‌بینید:

```
https://t.me/channelname/123
```

روی آیکون کپی کنار لینک کلیک کنید — همین، لینک کپی شد.

**راه دوم — از تلگرام:**
روی پست مورد نظر کلیک کنید، گزینه **Copy Link** رو بزنید.

**مرحله ۲ — Action رو اجرا کنید**

به تب **Actions** مخزن خود بروید:

1. روی **⬇️ Download Telegram Post** کلیک کنید
2. روی **Run workflow** کلیک کنید
3. لینک پست را داخل فیلد وارد کنید
4. **Run workflow** را بزنید

**مرحله ۳ — فایل رو دانلود کنید**

بعد از تموم شدن Action (معمولاً ۳۰ ثانیه تا چند دقیقه بسته به حجم فایل)، فایل داخل پوشه `downloads/` ذخیره میشه.

برای دانلود، روی اسم فایل کلیک کنید، بعد دکمه **Download raw file** رو بزنید.

```
downloads/
└── channelname_123_2026-01-01_12-00/
    ├── video/        ← ویدیوها
    ├── photo/        ← عکس‌ها
    ├── voice/        ← فایل‌های صوتی
    ├── file/         ← PDF و سایر فایل‌ها
    └── README.md     ← اطلاعات پست
```

---

## 📦 فایل‌های بزرگ (بالای ۱۰۰MB)

GitHub فایل‌های بالای ۱۰۰MB رو قبول نمی‌کنه. اگه فایل مورد نظرتون بزرگ باشه، به‌صورت خودکار به قطعات **۹۵MB** زیپ تقسیم میشه:

```
video.mp4.part001.zip
video.mp4.part002.zip
video.mp4.part003.zip
```

**برای بازیابی فایل اصلی:**

1. همه قطعات را دانلود کنید
2. هر قطعه را با **WinRAR** یا **7-Zip** استخراج کنید
3. تمام قطعات استخراج‌شده را کنار هم در یک پوشه بذارید
4. فایل اصلی بازیابی میشه

---

## 📁 ساختار کامل مخزن

```
Telegram-Mirror/
├── .github/
│   └── workflows/
│       ├── fetch.yml              ← اکشن Channel Reader
│       └── downloader.yml         ← اکشن Post Downloader
├── scripts/
│   ├── fetch_channel.py           ← اسکریپت خواندن کانال
│   └── download_post.py           ← اسکریپت دانلود پست
├── channels/
│   └── channel_1_2026-...md      ← فایل‌های کانال‌ها
├── downloads/
│   └── channelname_2_.../       ← فایل‌های دانلود شده
└── README.md
```

---

## ⚙️ پارامترها

**Channel Reader**

| پارامتر | پیش‌فرض | توضیح |
|:-------:|:-------:|:------|
| `channel` | — | نام کانال بدون `@` — اجباری |
| `count` | `100` | تعداد پیام — بین ۱۰ تا ۲۰۰ |

**Post Downloader**

| پارامتر | توضیح |
|:-------:|:------|
| `url` | لینک کامل پست تلگرام — اجباری |

---

## ⚠️ محدودیت‌ها

- فقط کانال‌های **عمومی** تلگرام پشتیبانی می‌شوند
- ویدیوها در فایل Markdown فقط به‌صورت لینک نمایش داده می‌شوند — برای دانلود از ابزار دوم استفاده کنید
- پوشه‌های `channels/` و `downloads/` را گاهی پاک‌سازی کنید تا مخزن سنگین نشود

---

## 🔄 آپدیت به نسخه جدید

برای همگام‌سازی فورک خودت با آخرین تغییرات ریپازیتوری اصلی، دکمه **Sync fork** رو در صفحه اصلی ریپازیتوریت در گیت‌هاب بزن.

---

## ⚠️ سلب مسئولیت

این پروژه برای استفاده شخصی جهت دسترسی به محتوا در محیط‌های با محدودیت شبکه طراحی شده. کاربران مسئول رعایت شرایط خدمات هر پلتفرم و قوانین کشور خود هستند.

---

## 📄 لایسنس

MIT License — آزاد برای استفاده شخصی

---

<div align="center">

ساخته شده با ❤️

---

اگه این پروژه برات مفید بود، با یه ⭐ حمایت کن تا به بقیه هم نشون داده بشه

<a href="https://star-history.com/#FALKON-CODE/Telegram-Mirror&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=FALKON-CODE/Telegram-Mirror&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=FALKON-CODE/Telegram-Mirror&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=FALKON-CODE/Telegram-Mirror&type=Date" />
  </picture>
</a>

</div>
