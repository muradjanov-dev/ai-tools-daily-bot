# 🤖 AI Tools Daily Bot (O'zbek tilida)

Har kuni Telegram kanalga eng yaxshi 5 ta AI tool haqida o'zbek tilida xabar yuboradi.

## ⚙️ Sozlash

### 1. GitHub Secrets qo'shish

GitHub repositoriyangizda **Settings → Secrets and variables → Actions** ga boring va quyidagilarni qo'shing:

| Secret nomi | Qiymati |
|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot tokeningiz (BotFatherdan) |
| `TELEGRAM_CHANNEL_ID` | Kanal ID (masalan: `-1001161187842`) |
| `ANTHROPIC_API_KEY` | Claude API kaliti (console.anthropic.com) |

### 2. Bot kanalga admin qo'shish

Telegram kanalingizda botni **Administrator** sifatida qo'shing.

### 3. Ishga tushirish

- **Avtomatik**: Har kuni soat 09:00 Toshkent vaqtida (UTC+5)
- **Qo'lda**: GitHub → Actions → "Daily AI Tools" → "Run workflow"

## 📋 Xabar formati

```
🤖 AI TOOLS KUNDALIGI
📅 Dushanba, 25.05.2026
━━━━━━━━━━━━━━━━━━━━

🎨 1. [Midjourney](https://midjourney.com)
_AI-powered image generation_

✅ Imkoniyatlari:
  • Yuqori sifatli rasmlar yaratish
  • Turli uslublar qo'llash
  • Tez rendering

🎯 Kimga foydali: Dizaynerlar va kontent yaratuvchilar
💛 Narx: Freemium

────────────────────
...
```

## 🔧 Texnologiyalar

- **Python 3.11**
- **Claude AI (Anthropic)** — toollarni topish va tarjima
- **Telegram Bot API** — xabar yuborish
- **GitHub Actions** — avtomatik ishlatish (bepul!)

## 📁 Fayl tuzilmasi

```
ai-tools-bot/
├── .github/
│   └── workflows/
│       └── daily_ai_tools.yml    # GitHub Actions
├── scripts/
│   └── ai_tools_bot.py           # Asosiy bot
├── requirements.txt
└── README.md
```
