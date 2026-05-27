# config.py - সব কনফিগারেশন

import logging
import os
from dotenv import load_dotenv
# লগিং বন্ধ (কনসোল ক্লিন রাখার জন্য)
logging.basicConfig(level=logging.ERROR)


load_dotenv()


# ==================== বট টোকেন (এনভায়রনমেন্ট থেকে) ====================
MAIN_BOT_TOKEN = os.getenv("MAIN_BOT_TOKEN")
FORWARD_BOT_TOKEN = os.getenv("FORWARD_BOT_TOKEN")

# ==================== অথোরাইজেশন টোকেন (এনভায়রনমেন্ট থেকে) ====================
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
# ==================== কাস্টম ইমোজি সেটআপ ====================
CUSTOM_EMOJI = {
    "☝️": "5370971163310693562",
    "🔍": "6230809013081086802",
    "📱": "5406809207947142040",
    "📞": "5467539229468793355",
    "📲": "5406809207947142040",
    "📧": "6066735296664315449",
    "📩": "5440411975509096877",
    "🔁": "6068952423207018572",
    "🖼": "5895654525787705071",
    "🔙": "6069102313270680292",
    "⚡️": "6068764024466579010",
    "✅": "6230828091325818369",
    "❌": "6232999605315837644",
    "⚠️": "6068825953600020820",
    "💡": "6231098605545986891",
    "📊": "6233241506463883080",
    "📁": "6068690460266733076",
    "📤": "5433614747381538714",
    "📥": "5433811242135331842",
    "🗑": "6233541449799966206",
    "👑": "6233184726996229549",
    "🔄": "6233525120334306978",
    "🔽": "6233121371933646400",
    "🆙": "5364105043907716258",
    "➕": "6232999738459823976",
    "📌": "6069019922913042683",
    "📝": "6068756607058058490",
    "📖": "5226512880362332956",
    "📂": "6068668585998295496",
    "📄": "5873153278023307367",
    "🔒": "5870704313440932932",
    "🎯": "5350460637182993292",
    "🏠": "5897974332113554932",
    "🔑": "5330115548900501467",
    "📦": "5348149223223211884",
    "🔢": "6069063503946193958",
    "1️⃣": "5305763715692377402",
    "2️⃣": "5307907239380528763",
    "3️⃣": "5305783000095537258",
    "▶️": "6233040536354168126",
    "📸": "6068757169698774770",
    "📚": "6068862933268438405",
    "⚙️": "5895577117592128901",
    "✨": "6233513150260454199",
    "🔵": "6231224366483384495",
     "📶": "6068879614921417014",
     "📡": "6231210205976206571",
     "🚀": "6233517642796245069",
     "▶": "6233094549862884974",
     "💥": "6069011470417402710",
    "🟢": "6068748090137911256",
    "🔴": "6233042091132329496",
    "⏳": "6068683476649911076",
    "🆔": "5841276284155467413",
    "📢": "6069037893056208851",
    "🚫": "6068656199312612368",
    "🌍": "6233278851204521733",
    "📍": "6069019922913042683",
    "💬": "6230972419406830926",
    "👥": "5372926953978341366",
    "👤": "6068906707575119126",
    "🤖": "6231151468003467518",
    "➤": "6066595151881445205",
    "👇": "6233121371933646400",
}


def emoji(emoji_char):
    """HTML ফরম্যাটে কাস্টম ইমোজি রিটার্ন করে
    
    ব্যবহার: 
        text = f"{emoji('✅')} Success!"
        await message.reply_text(text, parse_mode="HTML")
    """
    if emoji_char in CUSTOM_EMOJI:
        return f'<tg-emoji emoji-id="{CUSTOM_EMOJI[emoji_char]}">{emoji_char}</tg-emoji>'
    return emoji_char


# ==================== বট টোকেন ====================
#MAIN_BOT_TOKEN = "8643476914:AAGJ2G9ZbKz2-IiWrHZOmeyTJbG5OFsE74k"
#FORWARD_BOT_TOKEN = "8970483234:AAEUcr6_SbfQoMC2pTwzKZ9fjYUH9GxiEXU"

# ==================== গ্রুপ আইডি ====================
OTP_GROUP_ID = -1003981067662
RANGE_GROUP_ID = -1003958698384

# ==================== লিংক ====================
NUMBER_BOT_LINK = "https://t.me/SmsCenterX_bot"
MAIN_CHANNEL_LINK = "https://t.me/Team_X_Run"
RANGE_GROUP_LINK = "https://t.me/OtpRange24"
OTP_GROUP_LINK = "https://t.me/OtppGroup24"
# config.py - তে যোগ করুন
ADMIN_LINK = "https://t.me/Sadhan_Chakma"

# ==================== API এন্ডপয়েন্ট ====================
BASE_URL = "https://smscenter.io"

# ১. নম্বর রিকোয়েস্ট করার API (POST)
GET_NUMBER_URL = f"{BASE_URL}/api/freelancer/get-page/get-number"

# ২. OTP হিস্ট্রি API (GET) - এখানে OTP কোড আছে, কিন্তু country_name null
GET_OTP_HISTORY_URL = f"{BASE_URL}/api/freelancer/get-page?include=otp-history&page=1&limit=100"

# ৩. হিস্ট্রি API (GET) - এখানে country_name ও operator_name আছে, কিন্তু OTP কোড নেই
GET_HISTORY_URL = f"{BASE_URL}/api/freelancer/get-page?include=history&page=1&limit=100"

# ৪. টিম কনসোল API (GET) - Range Group এর জন্য
GET_CONSOLE_TEAM_URL = f"{BASE_URL}/api/freelancer/console/team?page=1&limit=20"

# ==================== অথোরাইজেশন টোকেন ====================
#AUTH_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjIyMywiZW1haWwiOiJzYWRoYW5jaGFrbWEwNTVAZ21haWwuY29tIiwicm9sZSI6ImZyZWVsYW5jZXIiLCJ1c2VybmFtZSI6IlNhZGhhbmNoYWttYWEiLCJpYXQiOjE3Nzk4MDU4NjMsImV4cCI6MTc3OTg5MjI2M30.rvA6i6kmOJfMa0EUG13qaU_DFuXEhIVzT46MDEiyFNI"

HEADERS = {
    "Authorization": AUTH_TOKEN,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 16; 2312DRA50G) AppleWebKit/537.36"
}

# ==================== টাইম সেটিংস ====================
NUMBER_EXPIRY_SECONDS = 600
OTP_CHECK_INTERVAL = 5
HIDE_DIGITS_COUNT = 5