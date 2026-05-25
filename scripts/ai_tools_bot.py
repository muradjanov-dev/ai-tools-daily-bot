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


def gemini_generate(prompt: str, max_tokens: int = 4000, json_mode: bool = True) -> str:
    """Gemini orqali matn yaratadi. JSON mode bilan to'g'ri JSON kafolat beradi"""
    config_kwargs = {
        "max_output_tokens": max_tokens,
        "temperature": 0.7,
    }
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"

    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(**config_kwargs)
    )

    # Tekshirish - javob bormi
    if not response.candidates or not response.candidates[0].content.parts:
        raise ValueError(f"Gemini bo'sh javob qaytardi. Finish reason: {response.candidates[0].finish_reason if response.candidates else 'none'}")

    content = response.text.strip()

    # Markdown code block tozalash (JSON mode da kelmasligi kerak, lekin xavfsizlik uchun)
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

Menga bugungi kunda eng yangi va foydali 3 ta AI tool haqida ma'lumot bering.
Fokus: {category} sohasidagi toollar.

Har bir tool uchun quyidagi formatda JSON yuboring:
{{
  "tools": [
    {{
      "name": "Tool nomi (asl inglizcha)",
      "url": "https://...",
      "emoji": "tegishli bitta emoji",
      "what": "Nima uchun (3-6 so'z, juda qisqa)",
      "who": "Kimlar uchun (2-3 ta kasb)",
      "tip": "Tavsiya (1 amaliy maslahat, max 8 so'z)"
    }}
  ]
}}

MISOL:
{{
  "name": "Otter.ai",
  "url": "https://otter.ai",
  "emoji": "🎙️",
  "what": "Yig'ilishlarni avto transkripsiya qilish",
  "who": "Menejerlar, jurnalistlar",
  "tip": "Zoom'ga ulang — xulosa beradi"
}}

QOIDALAR:
- Real toollar (2024-2025 mashhur), haqiqiy URL'lar
- Turli kompaniyalardan
- HAR JAVOB JUDA QISQA bo'lsin — uzun jumla yo'q
- Hech qanday emoji yoki '*' ishlatmang matn ichida

Faqat JSON qaytaring."""

    content = gemini_generate(prompt, max_tokens=4000)
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

    try:
        content = gemini_generate(prompt, max_tokens=3000)
        translations = json.loads(content).get("translations", [])
    except (json.JSONDecodeError, ValueError) as e:
        print(f"⚠️  Tarjima xatosi ({e}), inglizcha sarlavhalar ishlatiladi")
        translations = [item["title"] for item in news_items]

    result = []
    for item, translation in zip(news_items, translations):
        result.append({
            "headline": translation or item["title"],
            "url": item["url"],
            "source": item["source"]
        })

    return {"news": result}


def translate_to_uzbek(tools_data):
    """Tools ma'lumoti allaqachon o'zbek tilida prompt orqali so'ralgan, qaytaramiz"""
    return tools_data

def html_escape(text):
    """HTML xavfsiz qilish"""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_tools_message(tools_data):
    """AI Tools uchun xabar (HTML format)"""
    today = datetime.now().strftime("%d-%b")
    tools = tools_data.get("tools", [])

    message = f"🤖 <b>Ai bo'taloq {today}</b>\n\n"

    for tool in tools:
        emoji = tool.get("emoji", "🔧")
        name = html_escape(tool.get("name", ""))
        url = tool.get("url", "")
        what = html_escape(tool.get("what", ""))
        who = html_escape(tool.get("who", ""))
        tip = html_escape(tool.get("tip", tool.get("how", "")))

        message += f'{emoji} <a href="{url}"><b>{name}</b></a>\n'
        if what:
            message += f"🎯 <b>Nima uchun?</b> {what}\n"
        if who:
            message += f"👥 <b>Kimlar uchun?</b> {who}\n"
        if tip:
            message += f"💡 <b>Tavsiya:</b> {tip}\n"
        message += "\n"

    message += '<a href="https://t.me/ai_botaloq">@ai_botaloq</a> — ai botaloq bilan sun\'iy intellekt'
    return message


def format_news_message(news_data):
    """AI Yangiliklar uchun alohida xabar (HTML format)"""
    today = datetime.now().strftime("%d-%b")
    news = news_data.get("news", [])

    if not news:
        return None

    message = f"📰 <b>Ai bo'taloq {today}</b>\n\n"
    for item in news:
        headline = html_escape(item.get("headline", ""))
        n_url = item.get("url", "")
        message += f'● <a href="{n_url}">{headline}</a>\n\n'

    message += '<a href="https://t.me/ai_botaloq">@ai_botaloq</a> — ai botaloq bilan sun\'iy intellekt'
    return message

def send_to_telegram(message):
    """Telegramga xabar yuboradi"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
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

        # 4. Xabarlarni formatlash (alohida)
        print("\n📝 Xabarlar formatlanmoqda...")
        tools_msg = format_tools_message(tools_uz)
        news_msg = format_news_message(news_data)
        print(f"✅ Tools xabar: {len(tools_msg)} belgi")
        if news_msg:
            print(f"✅ News xabar: {len(news_msg)} belgi")

        # 5. Tools xabarini yuborish
        print("\n📤 AI Tools xabari yuborilmoqda...")
        success1 = send_to_telegram(tools_msg)

        # 6. News xabarini yuborish (alohida)
        success2 = True
        if news_msg:
            print("\n📤 AI News xabari yuborilmoqda...")
            success2 = send_to_telegram(news_msg)

        if success1 and success2:
            print("\n🎉 Hamma xabarlar muvaffaqiyatli yuborildi!")
        else:
            print("\n❌ Ba'zi xabarlarda xato yuz berdi")

    except Exception as e:
        error = str(e)
        print(f"\n❌ XATO: {error}")
        send_error_notification(error)
        raise

if __name__ == "__main__":
    main()
