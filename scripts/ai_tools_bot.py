#!/usr/bin/env python3
"""
AI Tools Daily Bot - Har kuni yangi AI toollarni Telegram kanalga yuboradi
"""

import os
import json
import random
import requests
import feedparser
from datetime import datetime, timedelta, timezone
from time import mktime
import google.generativeai as genai

# Ishonchli AI yangiliklar RSS manbalari
RSS_FEEDS = [
    ("OpenAI", "https://openai.com/blog/rss.xml"),
    ("Google DeepMind", "https://deepmind.google/blog/rss.xml"),
    ("Google Research", "https://research.google/blog/rss/"),
    ("Hugging Face", "https://huggingface.co/blog/feed.xml"),
    ("The Verge AI", "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
    ("MIT Tech Review AI", "https://www.technologyreview.com/topic/artificial-intelligence/feed"),
    ("Ars Technica AI", "https://arstechnica.com/ai/feed/"),
    ("Wired AI", "https://www.wired.com/feed/tag/ai/latest/rss"),
]

# Config
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHANNEL_ID = os.environ["TELEGRAM_CHANNEL_ID"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

genai.configure(api_key=GEMINI_API_KEY)
# Gemini 2.5 Flash - bepul tier, tez va arzon
model = genai.GenerativeModel("gemini-2.5-flash")


def gemini_generate(prompt: str, max_tokens: int = 2000) -> str:
    """Gemini orqali matn yaratadi va JSON ni tozalaydi"""
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=0.7,
        )
    )
    content = response.text.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
    return content

def search_ai_tools():
    """Claude orqali bugungi eng yaxshi AI toollarni topadi"""
    today = datetime.now().strftime("%Y-%m-%d")

    # Har kuni boshqa kategoriyalarga fokus qilish uchun
    categories = [
        "productivity va ish samaradorligi",
        "kod yozish va dasturlash",
        "rasm va video yaratish",
        "matn yozish va kontent",
        "biznes va marketing",
        "ta'lim va o'rganish",
        "ovoz va musiqa",
        "ma'lumot tahlili",
    ]

    day_of_week = datetime.now().weekday()
    category = categories[day_of_week % len(categories)]

    prompt = f"""Siz AI texnologiyalar mutaxassisisiz. Bugun {today}.

Menga bugungi kunda eng yangi, qiziqarli va foydali 5 ta AI tool haqida ma'lumot bering.
Fokus: {category} sohasidagi toollar.

Har bir tool uchun quyidagi formatda JSON yuboring:
{{
  "tools": [
    {{
      "name": "Tool nomi",
      "url": "https://...",
      "emoji": "tegishli emoji",
      "tagline": "qisqa slogan (inglizcha)",
      "features": [
        "asosiy xususiyat (qisqa, 5-8 so'z)"
      ],
      "use_cases": "kim foydalanishi (qisqa)",
      "pricing": "bepul/pullik/freemium",
      "category": "{category}"
    }}
  ]
}}

MUHIM TALABLAR:
- Real va mavjud toollar bo'lsin (2024-2025 yillarda chiqgan yoki mashhur bo'lgan)
- Har bir tool haqiqiy URL ga ega bo'lsin
- Turli-xil toollar tanlang (bir xil kompaniyadan emas)
- Chindan ham foydali va qiziqarli toollar tanlang

Faqat JSON qaytaring, boshqa matn yo'q."""

    content = gemini_generate(prompt, max_tokens=2000)
    return json.loads(content)


def fetch_real_ai_news(max_items=5, hours_back=72):
    """Haqiqiy RSS manbalardan AI yangiliklarini oladi"""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    all_items = []

    for source_name, feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url, request_headers={
                "User-Agent": "Mozilla/5.0 (compatible; AIToolsBot/1.0)"
            })
            for entry in feed.entries[:5]:
                pub_date = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    pub_date = datetime.fromtimestamp(mktime(entry.published_parsed), tz=timezone.utc)
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    pub_date = datetime.fromtimestamp(mktime(entry.updated_parsed), tz=timezone.utc)

                if pub_date and pub_date < cutoff:
                    continue

                title = entry.get("title", "").strip()
                url = entry.get("link", "").strip()

                if not title or not url:
                    continue

                all_items.append({
                    "title": title,
                    "url": url,
                    "source": source_name,
                    "date": pub_date or datetime.now(timezone.utc)
                })
            print(f"  ✓ {source_name}: {len(feed.entries)} ta entry")
        except Exception as e:
            print(f"  ✗ {source_name}: {e}")

    # Sort by date, newest first
    all_items.sort(key=lambda x: x["date"], reverse=True)

    # Dedupe by title prefix (avoid same news from multiple sources)
    seen_titles = set()
    unique = []
    for item in all_items:
        key = item["title"][:50].lower()
        if key in seen_titles:
            continue
        seen_titles.add(key)
        unique.append(item)

    return unique[:max_items]


def translate_news_to_uzbek(news_items):
    """Inglizcha sarlavhalarni o'zbek tiliga tarjima qiladi"""
    if not news_items:
        return {"news": []}

    titles_text = "\n".join([
        f"{i+1}. {item['title']}" for i, item in enumerate(news_items)
    ])

    prompt = f"""Quyidagi haqiqiy AI yangiliklar sarlavhalarini O'ZBEK tiliga tarjima qiling.

{titles_text}

QOIDALAR:
📰 Tabiiy, rasmiy o'zbek tilida tarjima qiling
📰 Faqat tarjima qiling — MA'NOSINI O'ZGARTIRMANG, qo'shimcha narsa qo'shmang
📰 Kompaniya, mahsulot va odam nomlarini (OpenAI, ChatGPT, Sam Altman) o'zgartirmang
📰 Tarjima 8-15 so'zdan iborat bo'lsin
📰 Clickbait emas — rasmiy, jurnalistik ohang
📰 Texnik atamalarni tushunarli qiling, lekin aniqlikni saqlang

Format - faqat JSON:
{{
  "translations": [
    "1-tarjima",
    "2-tarjima",
    ...
  ]
}}

Faqat JSON qaytaring, hech narsa qo'shmang."""

    content = gemini_generate(prompt, max_tokens=1500)
    translations = json.loads(content).get("translations", [])

    result = []
    for item, translation in zip(news_items, translations):
        result.append({
            "headline": translation,
            "url": item["url"],
            "source": item["source"]
        })

    return {"news": result}


def translate_to_uzbek(tools_data):
    """Toollar ma'lumotini o'zbek tiliga tarjima qiladi"""
    tools_json = json.dumps(tools_data, ensure_ascii=False, indent=2)

    prompt = f"""Quyidagi AI toollar haqidagi ma'lumotni O'ZBEK tiliga tarjima qiling.

{tools_json}

Qoidalar:
- features va use_cases ni o'zbek tiliga tarjima qiling
- name, url, emoji, tagline, pricing ni o'zgartirmang
- category ni ham o'zbek tilida yozing
- Tarjima tabiiy va tushunarli bo'lsin
- IT atamalarini (AI, tool, app va h.k.) saqlab qolish mumkin

Faqat JSON formatida qaytaring."""

    content = gemini_generate(prompt, max_tokens=2000)
    return json.loads(content)

def format_telegram_message(tools_data, news_data):
    """Telegram uchun qisqa xabar formatlaydi"""
    today = datetime.now().strftime("%d.%m.%Y")
    tools = tools_data.get("tools", [])
    news = news_data.get("news", [])

    message = f"🤖 *AI TOOLS — {today}*\n\n"

    for tool in tools:
        emoji = tool.get("emoji", "🔧")
        name = tool.get("name", "")
        url = tool.get("url", "")
        features = tool.get("features", [])
        pricing = tool.get("pricing", "").lower()

        price_icon = "💚" if "free" in pricing or "bepul" in pricing else \
                     "💛" if "freemium" in pricing else "💰"

        main_feature = features[0] if features else ""

        message += f"{emoji} [*{name}*]({url}) {price_icon}\n"
        if main_feature:
            message += f"   _{main_feature}_\n"
        message += "\n"

    if news:
        message += "━━━━━━━━━━━━━━━\n"
        message += f"📰 *AI DAYJEST — {today}*\n\n"
        for item in news:
            headline = item.get("headline", "")
            n_url = item.get("url", "")
            source = item.get("source", "")
            message += f"● [{headline}]({n_url})\n"
            if source:
                message += f"   _Manba: {source}_\n"
            message += "\n"

    message += "#AITools #AINews #Uzbek"
    return message

def send_to_telegram(message):
    """Telegramga xabar yuboradi"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }

    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()

    result = response.json()
    if result.get("ok"):
        print(f"✅ Xabar muvaffaqiyatli yuborildi! Message ID: {result['result']['message_id']}")
        return True
    else:
        print(f"❌ Xato: {result}")
        return False

def send_error_notification(error_msg):
    """Xato bo'lganda xabar yuboradi"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": f"⚠️ Bot xatosi: {error_msg}",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def main():
    print("🚀 AI Tools Bot ishga tushdi...")
    print(f"📅 Sana: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    try:
        # 1. AI toollarni qidirish
        print("\n🔍 AI toollar qidirilmoqda...")
        tools_data = search_ai_tools()
        print(f"✅ {len(tools_data.get('tools', []))} ta tool topildi")

        # 2. O'zbek tiliga tarjima
        print("\n🇺🇿 O'zbek tiliga tarjima qilinmoqda...")
        tools_uz = translate_to_uzbek(tools_data)
        print("✅ Tarjima tugadi")

        # 3. Haqiqiy RSS dan AI yangiliklarni olish
        print("\n📰 RSS manbalardan AI yangiliklari olinmoqda...")
        try:
            real_news = fetch_real_ai_news(max_items=5, hours_back=72)
            print(f"✅ {len(real_news)} ta haqiqiy yangilik topildi")
            print("\n🌐 Sarlavhalar o'zbek tiliga tarjima qilinmoqda...")
            news_data = translate_news_to_uzbek(real_news)
            print(f"✅ {len(news_data.get('news', []))} ta yangilik tarjima qilindi")
        except Exception as e:
            print(f"⚠️  Yangiliklar olinmadi: {e}")
            news_data = {"news": []}

        # 4. Xabarni formatlash
        print("\n📝 Xabar formatlanmoqda...")
        message = format_telegram_message(tools_uz, news_data)
        print(f"✅ Xabar tayyor ({len(message)} belgi)")

        # Debug: xabarni ko'rsatish
        print("\n" + "="*50)
        print("TELEGRAM XABARI PREVIEW:")
        print("="*50)
        print(message)
        print("="*50 + "\n")

        # 4. Telegramga yuborish
        print("📤 Telegramga yuborilmoqda...")
        success = send_to_telegram(message)

        if success:
            print("\n🎉 Hammasi muvaffaqiyatli bajarildi!")
        else:
            print("\n❌ Xabar yuborishda xato yuz berdi")

    except Exception as e:
        error = str(e)
        print(f"\n❌ XATO: {error}")
        send_error_notification(error)
        raise

if __name__ == "__main__":
    main()
