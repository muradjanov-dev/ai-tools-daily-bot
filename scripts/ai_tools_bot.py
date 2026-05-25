#!/usr/bin/env python3
"""
AI Tools Daily Bot - Har kuni yangi AI toollarni Telegram kanalga yuboradi
"""

import os
import json
import random
import requests
from datetime import datetime
from anthropic import Anthropic

# Config
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHANNEL_ID = os.environ["TELEGRAM_CHANNEL_ID"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

client = Anthropic()

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

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.content[0].text.strip()

    # JSON ni tozalash
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    return json.loads(content)

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

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.content[0].text.strip()

    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    return json.loads(content)

def format_telegram_message(tools_data):
    """Telegram uchun qisqa xabar formatlaydi"""
    today = datetime.now().strftime("%d.%m.%Y")
    tools = tools_data.get("tools", [])

    message = f"🤖 *AI TOOLS — {today}*\n\n"

    for i, tool in enumerate(tools, 1):
        emoji = tool.get("emoji", "🔧")
        name = tool.get("name", "")
        url = tool.get("url", "")
        features = tool.get("features", [])
        pricing = tool.get("pricing", "").lower()

        price_icon = "💚" if "free" in pricing or "bepul" in pricing else \
                     "💛" if "freemium" in pricing else "💰"

        # Faqat 1 ta eng muhim xususiyat
        main_feature = features[0] if features else ""

        message += f"{emoji} [*{name}*]({url}) {price_icon}\n"
        if main_feature:
            message += f"   _{main_feature}_\n"
        message += "\n"

    message += "#AITools #Uzbek"
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

        # 3. Xabarni formatlash
        print("\n📝 Xabar formatlanmoqda...")
        message = format_telegram_message(tools_uz)
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
