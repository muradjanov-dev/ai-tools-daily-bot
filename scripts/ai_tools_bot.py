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

⚠️ DIQQAT — BU BIZNING BENZARSIZ BRENDIMIZ:

Biz "Ai bo'taloq" kanalimiz. Donishmand bobo, hazil-qiyofa amaki va falsafiy do'st bir tanada yashaydi.
O'qigan kishi: "Voy, bu boshqacha-ku!" desin. Asli — yodda qolaylik.

🎭 OHANG (eng muhimi):
- Falsafiy, donishmand, biroz hazil — quruq texnik tavsif EMAS
- Har jumla — kichik hayot bo'lagi yoki kuzatuv kabi
- Ba'zan ritorik savol: "ko'rdingizmi?", "to'g'rimi?", "ha?", "labbay?"
- Ba'zan kichik metafora: "bo'sh qog'oz qo'rquvi", "vaqt — daryo", "so'zlar havoga sochiladi"
- Ba'zan to'g'ridan-to'g'ri haqiqat: "shuncha vaqtni biror narsaga sarflagansiz, ko'rasiz endi..."
- "Siz" deb murojaat — go'yo eski tanish bilan suhbat

💝 MEHRLI MUROJAATLAR — HAR TOOLDA ISHLATING:
Quyidagi so'zlardan tanlang va har bir tool tavsifida HECH BO'LMAGANDA 1 marta ishlating:
- bo'talog'im, qo'zichog'im, do'mboqqinam
- qadrligim, himmatligim, yulduzim
- peshqadamim, chempionim, shijoatligim

⚡ MUHIM QOIDALAR:
- Har 3 ta toolda BOSHQA-BOSHQA so'z (takrorlanmasin)
- So'z tanlash kontekstga mos bo'lsin:
  • Mehnat/g'alaba tooli → "chempionim", "shijoatligim", "peshqadamim"
  • Ijodiy tool → "yulduzim", "qadrligim"
  • Oddiy/iliq tool → "qo'zichog'im", "bo'talog'im", "do'mboqqinam"
  • Hayotiy/falsafiy → "himmatligim"
- O'rni har xil: ba'zan jumla boshida, ba'zan o'rtada, ba'zan oxirida
- "what", "who", "tip" — istalganida joylashtirsa bo'ladi
- Sun'iy emas, tabiiy yangrasin

TO'LIQ MISOL (har birida mehrli murojaat — har xil):

{{
  "name": "Otter.ai",
  "url": "https://otter.ai",
  "emoji": "🎙️",
  "what": "Yig'ilishdagi so'zlar havoda sochilmasin, qog'ozga tushiradi.",
  "who": "Ko'p uchrashuvga kiradiganlar — boshliq, sotuvchi, jurnalist.",
  "tip": "Zoom'ga ulang — xulosa o'zi keladi, qo'zichog'im."
}}

{{
  "name": "Notion AI",
  "url": "https://www.notion.so/product/ai",
  "emoji": "✍️",
  "what": "Bo'sh qog'oz qo'rquvi yo'q endi, yulduzim — aytasiz, yozadi.",
  "who": "Yozadigan har kim: talaba, blog yozuvchi, ofis xodimi.",
  "tip": "\"/\" bosing va istagingizni so'zlar bilan ayting."
}}

{{
  "name": "Cursor",
  "url": "https://cursor.com",
  "emoji": "💻",
  "what": "Kod yozish endi suhbatga aylangan, ko'rdingizmi?",
  "who": "Dasturchilar va dasturchi bo'lmoqchilar — chempionim, vaqtni tejaysiz.",
  "tip": "Cmd+K bosing va o'z tilingizda gapiring — eshitadi."
}}

🧒 SODDA TIL, LEKIN CHUQUR MA'NO:
- 5-6 yoshli bola ham tushunsin, lekin donishmand ham bosh chayqasin
- Texnik atamalar yo'q: "AI" → "aqlli yordamchi", "model" → "aqlli mashina"
- Har jumla yozishdan oldin: "Bu jumla ichida kichik bir hikmat bormi?" — sinov

🎯 UZUNLIK (qisqa, lekin yodda qoladigan):
- "what" — 1 ta jumla (qisqa hikoya yoki o'tkir kuzatuv)
- "who" — 1 ta jumla (qisqa, lekin xarakter bilan)
- "tip" — 1 ta jumla (aniq amaliy harakat)

UZUN TAVSIF YO'Q. Lekin har jumla — yodda qoladigan, hikmatli.

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

    translations = []
    for attempt in range(3):
        try:
            content = gemini_generate(prompt, max_tokens=3000)
            translations = json.loads(content).get("translations", [])
            if len(translations) == len(news_items):
                break
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Tarjima urinish #{attempt+1} xato: {e}")
            continue

    if len(translations) != len(news_items):
        print(f"⚠️  Tarjima muvaffaqiyatsiz — alohida tarjima qilamiz")
        translations = []
        for item in news_items:
            single_prompt = f"""Bu inglizcha AI yangilik sarlavhasini O'ZBEK tiliga kreativ tarjima qiling.
JURNALISTIK uslub: 8-12 so'z, INFORMATIV.

Sarlavha: {item['title']}

Faqat o'zbekcha tarjimani qaytaring, hech narsa qo'shmang."""
            try:
                t = gemini_generate(single_prompt, max_tokens=200, json_mode=False).strip().strip('"').strip()
                translations.append(t if t else item["title"])
            except Exception:
                translations.append(item["title"])

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

    message = f"🤖 <b>Ai bo'taloq {today}</b>\n\n"
    message += "<i>Bugungi AI yordamchilar</i>\n\n\n"

    for tool in tools:
        emoji = tool.get("emoji", "🔧")
        name = html_escape(tool.get("name", ""))
        url = tool.get("url", "")
        what = html_escape(tool.get("what", ""))
        who = html_escape(tool.get("who", ""))
        tip = html_escape(tool.get("tip", tool.get("how", "")))

        message += f'{emoji} <a href="{url}"><b>{name}</b></a>\n\n'
        if what:
            message += f"🎯 <b>Nima uchun?</b> {what}\n\n"
        if who:
            message += f"👥 <b>Kimlar uchun?</b> {who}\n\n"
        if tip:
            message += f"💡 <b>Tavsiya:</b> {tip}\n"
        message += "\n— — — — — — — — —\n\n"

    message += '<a href="https://t.me/ai_botaloq">@ai_botaloq</a> - sodda tilda sun\'iy intellekt'
    return message


def format_news_message(news_data):
    """AI Yangiliklar uchun alohida xabar (HTML format) — ertalab"""
    today = datetime.now().strftime("%d-%b")
    news = news_data.get("news", [])

    if not news:
        return None

    message = f"📰 <b>Ai bo'taloq {today}</b>\n\n"
    message += "<i>Bugungi AI yangiliklari</i>\n\n\n"

    for item in news:
        headline = html_escape(item.get("headline", ""))
        n_url = item.get("url", "")
        message += f'🧩 <a href="{n_url}">{headline}</a>\n\n'

    message += '\n<a href="https://t.me/ai_botaloq">@ai_botaloq</a> - sodda tilda sun\'iy intellekt'
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


def select_top_news(all_news, top_n=5):
    """20+ ta yangilikdan eng muhim 5 tasini Gemini orqali tanlaydi"""
    if len(all_news) <= top_n:
        return all_news

    news_list = "\n".join([
        f"{i+1}. [{item['source']}] {item['title']}"
        for i, item in enumerate(all_news)
    ])

    prompt = f"""Siz AI yangiliklar muharririsiz. Quyidagi {len(all_news)} ta yangilikdan
ENG MUHIM, ENG QIZIQARLI VA ENG TA'SIRLI {top_n} tasini tanlang.

{news_list}

TANLOV MEZONLARI:
1. Katta kompaniyalardan muhim e'lon (OpenAI, Google, Anthropic, Meta, Microsoft, xAI, DeepSeek)
2. Yangi mahsulot/model chiqishi
3. Kattalik: pul, raqam, ko'lam (milliardlar, millionlar)
4. Texnologiyaning hayotga ta'siri
5. Sodir bo'lgan voqea (kelajakdagi spekulyatsiya emas)

KAMROQ AHAMIYATLI:
- Mavhum tahlillar
- "X kompaniya Y haqida o'yladi" turidagi
- Reklama xarakteridagi
- Juda mahalliy/torcha yangiliklar

Faqat JSON qaytaring:
{{
  "selected": [1, 4, 7, 12, 15]
}}

Bu raqamlar — yuqoridagi ro'yxatdagi yangiliklarning RAQAMI (1-{len(all_news)})."""

    try:
        content = gemini_generate(prompt, max_tokens=500)
        indices = json.loads(content).get("selected", [])
        selected = []
        for idx in indices[:top_n]:
            i = idx - 1
            if 0 <= i < len(all_news):
                selected.append(all_news[i])
        if selected:
            return selected
    except Exception as e:
        print(f"⚠️  Tanlov xato ({e}), eng yangilarini olamiz")

    return all_news[:top_n]


def send_news():
    """AI Yangiliklar xabarini yuboradi (ertalab)"""
    print("\n📰 RSS manbalardan AI yangiliklari olinmoqda...")
    all_news = fetch_real_ai_news(max_items=20, hours_back=48)
    print(f"✅ {len(all_news)} ta yangilik topildi")

    print(f"\n🎯 Eng muhim 5 tasi tanlanmoqda...")
    top_news = select_top_news(all_news, top_n=5)
    print(f"✅ Top {len(top_news)} ta tanlandi")

    print("\n🌐 Sarlavhalar tarjima qilinmoqda...")
    news_data = translate_news_to_uzbek(top_news)
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
