# test_with_api.py - WhatsApp ইমোজি + API কল টেস্ট

import asyncio
import requests
from telegram import Bot

# ==================== কনফিগারেশন ====================
BOT_TOKEN = "8643476914:AAGJ2G9ZbKz2-IiWrHZOmeyTJbG5OFsE74k"  # আপনার বট টোকেন
CHAT_ID = "1919672730"  # আপনার চ্যাট আইডি

# API কনফিগারেশন
BASE_URL = "https://smscenter.io"
AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjIyMywiZW1haWwiOiJzYWRoYW5jaGFrbWEwNTVAZ21haWwuY29tIiwicm9sZSI6ImZyZWVsYW5jZXIiLCJ1c2VybmFtZSI6IlNhZGhhbmNoYWttYWEiLCJpYXQiOjE3Nzk4MDU4NjMsImV4cCI6MTc3OTg5MjI2M30.rvA6i6kmOJfMa0EUG13qaU_DFuXEhIVzT46MDEiyFNI"

HEADERS = {
    "Authorization": AUTH_TOKEN,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 16; 2312DRA50G) AppleWebKit/537.36"
}

# কাস্টম ইমোজি
WHATSAPP_EMOJI_ID = "6210911297182113031"

def whatsapp_emoji():
    return f'<tg-emoji emoji-id="{WHATSAPP_EMOJI_ID}">💚</tg-emoji>'


async def test_api_and_emoji():
    """API কল করে ডাটা এনে WhatsApp ইমোজি সহ দেখানো"""
    bot = Bot(token=BOT_TOKEN)
    
    # 1. API কল করা
    print("🔄 Calling API...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/freelancer/console/team?page=1&limit=5",
            headers=HEADERS,
            timeout=30
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            otps = data.get("data", [])
            print(f"✅ Got {len(otps)} OTPs from API")
            
            # 2. API থেকে পাওয়া ডাটা দেখানো
            if otps:
                first_otp = otps[0]
                service = first_otp.get("provider", "Unknown")
                
                message = f"""✨ <b>API Test Result</b> ✨

━━━━━━━━━━━━━━━━━━━━━━━

{whatsapp_emoji()} <b>Service from API:</b> {service}

📱 <b>Number:</b> <code>{first_otp.get('phone_number', 'Unknown')}</code>

🔑 <b>OTP:</b> <code>{first_otp.get('otp_code', 'Unknown')}</code>

🌍 <b>Country:</b> {first_otp.get('country_name', 'Unknown')}

━━━━━━━━━━━━━━━━━━━━━━━

{whatsapp_emoji()} <i>WhatsApp Custom Emoji Test with API</i>"""
                
                await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="HTML")
                print("✅ Message sent to Telegram!")
            else:
                print("⚠️ No OTP data from API")
                await bot.send_message(chat_id=CHAT_ID, text="⚠️ No OTP data from API", parse_mode="HTML")
        else:
            print(f"❌ API Error: {response.status_code}")
            await bot.send_message(chat_id=CHAT_ID, text=f"❌ API Error: {response.status_code}", parse_mode="HTML")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        await bot.send_message(chat_id=CHAT_ID, text=f"❌ Error: {e}", parse_mode="HTML")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════╗
║   API + WhatsApp Custom Emoji Test   ║
╚══════════════════════════════════════╝
    """)
    asyncio.run(test_api_and_emoji())