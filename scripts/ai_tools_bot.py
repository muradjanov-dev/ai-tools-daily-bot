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

    prompt = f"""Siz iliq, donishmand mentor uslubida yozadigan AI maslahatchisiz. Bugun {today}.

Bugungi kunda eng yangi va foydali 3 ta AI tool haqida ma'lumot bering.
Fokus: {category} sohasidagi toollar.

YOZUV USLUBI — BU BIZNING BRENDIMIZ:

🎨 Biz "Ai bo'taloq" kanalimiz — o'qigan har bir kishi bizni esda saqlab qolsin.
Bu — boshqa hech qaysi kanalda yo'q UNIKAL ohang:
- Donishmand bobo + qiziqarli amaki + falsafiy do'st aralashmasi
- Kulgili, g'ayrioddiy, lekin chuqur ma'noli
- Texnik emas — bolakaylar va donishmandlar bir xil tushunsin

🎯 SODDA TIL:
- 5-6 yoshli bolaga aytgandek tushuntiring
- "AI" → "aqlli yordamchi" / "aqlli mashina"
- "Transcription" → "eshitib, qog'ozga tushiradi"
- "Generate" → "yaratadi", "tug'iradi"
- Bobomiz ham, talaba ham tushunsin

🎯 ILIQLIK + G'AYRIODDIYLIK:
- "qo'zichog'im / bo'talog'im / qadrligim / yulduzim / do'mboqqinam / himmatligim" — FAQAT 1 ta toolda (3 dan birida), har gal BOSHQACHA so'z
- Qolgan 2 toolda — mehrli murojaatsiz, lekin baribir o'ziga xos ohang
- Ba'zan ritorik savol: "to'g'rimi?", "ko'rdingizmi?", "ha?"
- Ba'zan kichik kuzatuv-haqiqat: "vaqt og'rir narsa..."
- "siz" deb murojaat

🎯 ESDA QOLISH:
- Har gap shunday yozilsinki, odamlar uni do'stiga aytib bersa qiziqarli bo'lsin
- Quruq texnik tavsif emas — kichik hayot bo'lagidek

USLUB MISOLLARI (xuddi shunday — bolaga aytgandek):

1-MISOL (sodda + bitta murojaat):
{{
  "name": "Otter.ai",
  "url": "https://otter.ai",
  "emoji": "🎙️",
  "what": "Yig'ilishlaringizni eshitib, hammasini qog'ozga yozib beradi. Endi qo'lda yozish shart emas, qo'zichog'im.",
  "who": "Ko'p uchrashuv qiladiganlar — boshliq, sotuvchi, jurnalist",
  "tip": "Telefoningizga yuklab, gaplashayotganingizda qo'yib qo'ying"
}}

2-MISOL (toza sodda):
{{
  "name": "Notion AI",
  "url": "https://www.notion.so/product/ai",
  "emoji": "✍️",
  "what": "Sizning o'rningizga xat, eslatma, ro'yxat yozib beradi. Hatto she'r ham!",
  "who": "Yozadigan har kim — talaba, blog yozuvchi, ishchi",
  "tip": "Bo'sh joyga / belgisini bosing va nima xohlasangiz ayting"
}}

3-MISOL (juda sodda):
{{
  "name": "Cursor",
  "url": "https://cursor.com",
  "emoji": "💻",
  "what": "Kompyuter dasturi yozishni o'z tilingizda gapirib bajaradi. Aytasiz — yozadi.",
  "who": "Dasturchilar va dasturchi bo'lmoqchilar",
  "tip": "Ekranga qarab \"menga oddiy kalkulyator yoz\" deyish kifoya"
}}

QOIDALAR:
- Real toollar (2024-2025 mashhur), haqiqiy URL'lar, turli kompaniyalardan
- Har bir jumla — sodda, oddiy hayot so'zlari
- Texnik atamalar AVTOMATIK tarjima: "API"="ulanish", "model"="aqlli yordamchi", "transcription"="ovozni yozish"
- 3 ta tooldan FAQAT BITTASIDA mehrli murojaat (har gal boshqa so'z)
- Maydonlar ichida '*' yoki qo'shimcha emoji bo'lmasin

Format JSON:
{{
  "tools": [
    {{ "name": "...", "url": "...", "emoji": "...", "what": "...", "who": "...", "tip": "..." }}
  ]
}}

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

    prompt = f"""Siz 30 yillik tajribaga ega kreativ kopirayter va jurnalistsiz.
Quyidagi haqiqiy AI yangiliklar sarlavhalarini O'ZBEK tiliga PROFESSIONAL tarjima qiling.

{titles_text}

USLUB - MASTAVA DAYJEST kabi:
✓ "Amazon'dan yangi AI gadjet: Bee doimiy ravishda sizni eshitib turadi"
✓ "Xitoyning DeepSeek kompaniyasi AI narxlarini 75 foizga tushirdi"
✓ "San-Fransiskoda robotlar muhtojlar uchun ovqat tayyorlashni boshladi"
✓ "Xakerlar AI chatbotlarning «xarakterini» o'rganib, ularni aldashmoqda"
✓ "Siz ishlatayotgan xizmat haqiqatdan AI'mi yoki shunchaki reklama?"

QOIDALAR:
📰 Sarlavha 8-15 so'z — qisqa, lekin INFORMATIV
📰 Aniq raqam, nom, joy — eng muhimi sarlavhadan ko'rinsin
📰 Ba'zan ":" bilan struktura — "[Manba/Kontekst]: [Asosiy ma'lumot]"
📰 Ba'zan savol shaklida — qiziqish uyg'otish
📰 Kreativ lekin to'g'ri — sensatsiya emas
📰 Kompaniya/mahsulot nomlarini saqlang
📰 Tabiiy o'zbek tilida — gazeta jurnalisti kabi

MUHIM: Har sarlavha BOSHQACHA tuzilsin — bir xil shablon emas:
- birida ":" bilan
- birida savol
- birida to'g'ridan-to'g'ri
- birida joy/raqam ta'kidlangan

Format - faqat JSON:
{{
  "translations": [
    "1-professional tarjima",
    "2-professional tarjima",
    ...
  ]
}}

Faqat JSON qaytaring."""

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
    """AI Tools uchun xabar (HTML format) — kechqurun"""
    today = datetime.now().strftime("%d-%b")
    tools = tools_data.get("tools", [])

    message = f"🤖 <b>Ai bo'taloq {today}</b>\n"
    message += "<i>Bugungi AI yordamchilar</i>\n\n"

    for tool in tools:
        emoji = tool.get("emoji", "🔧")
        name = html_escape(tool.get("name", ""))
        url = tool.get("url", "")
        what = html_escape(tool.get("what", ""))
        who = html_escape(tool.get("who", ""))
        tip = html_escape(tool.get("tip", tool.get("how", "")))

        message += f'{emoji} <a href="{url}"><b>{name}</b></a>\n\n'
        if what:
            message += f"<b>Nima uchun?</b>\n{what}\n\n"
        if who:
            message += f"<b>Kimlar uchun?</b>\n{who}\n\n"
        if tip:
            message += f"<b>Tavsiya:</b>\n{tip}\n"
        message += "\n— — — — — — — — —\n\n"

    message += '<a href="https://t.me/ai_botaloq">@ai_botaloq</a> - bilan sun\'iy intellekt'
    return message


def format_news_message(news_data):
    """AI Yangiliklar uchun alohida xabar (HTML format) — ertalab"""
    today = datetime.now().strftime("%d-%b")
    news = news_data.get("news", [])

    if not news:
        return None

    message = f"📰 <b>Ai bo'taloq {today}</b>\n"
    message += "<i>Bugungi AI yangiliklari</i>\n\n"

    for item in news:
        headline = html_escape(item.get("headline", ""))
        n_url = item.get("url", "")
        message += f'🧩 <a href="{n_url}">{headline}</a>\n\n'

    message += '\n<a href="https://t.me/ai_botaloq">@ai_botaloq</a> - bilan sun\'iy intellekt'
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

def send_tools():
    """AI Tools xabarini yuboradi (kechqurun)"""
    print("\n🔍 AI toollar qidirilmoqda...")
    tools_data = search_ai_tools()
    print(f"✅ {len(tools_data.get('tools', []))} ta tool topildi")

    tools_uz = translate_to_uzbek(tools_data)
    tools_msg = format_tools_message(tools_uz)
    print(f"✅ Tools xabar tayyor: {len(tools_msg)} belgi")

    print("\n📤 AI Tools xabari yuborilmoqda...")
    return send_to_telegram(tools_msg)


def send_news():
    """AI Yangiliklar xabarini yuboradi (ertalab)"""
    print("\n📰 RSS manbalardan AI yangiliklari olinmoqda...")
    real_news = fetch_real_ai_news(max_items=5, hours_back=72)
    print(f"✅ {len(real_news)} ta yangilik topildi")

    print("\n🌐 Sarlavhalar tarjima qilinmoqda...")
    news_data = translate_news_to_uzbek(real_news)
    news_msg = format_news_message(news_data)

    if not news_msg:
        print("⚠️  Yuborish uchun yangilik yo'q")
        return False

    print(f"✅ News xabar tayyor: {len(news_msg)} belgi")
    print("\n📤 AI News xabari yuborilmoqda...")
    return send_to_telegram(news_msg)


def main():
    mode = os.environ.get("MODE", "both").lower()
    print(f"🚀 AI Tools Bot ishga tushdi — MODE: {mode}")
    print(f"📅 Sana: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    try:
        if mode == "tools":
            success = send_tools()
        elif mode == "news":
            success = send_news()
        else:  # both
            s1 = send_tools()
            s2 = send_news()
            success = s1 and s2

        if success:
            print("\n🎉 Muvaffaqiyatli yakunlandi!")
        else:
            print("\n❌ Xato bilan yakunlandi")

    except Exception as e:
        error = str(e)
        print(f"\n❌ XATO: {error}")
        send_error_notification(error)
        raise

if __name__ == "__main__":
    main()
