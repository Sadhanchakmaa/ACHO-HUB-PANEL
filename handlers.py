# handlers.py - সব হ্যান্ডলার (শুধু লাস্ট OTP Range Group এ পাঠাবে)

import time
import asyncio
from typing import Dict, List
from cleaner import track_message

from telegram import Update, Bot, InlineKeyboardButton, CopyTextButton
from telegram.ext import CallbackContext
from telegram.error import BadRequest

from config import (
    MAIN_BOT_TOKEN, FORWARD_BOT_TOKEN,
    OTP_GROUP_ID, RANGE_GROUP_ID,
    OTP_CHECK_INTERVAL,
    emoji
)
from utils import *
from keyboards import *
# handlers.py - এর শুরুতে ইম্পোর্ট যোগ করুন
from utils import get_social_emoji  # ← এই লাইন যোগ করুন

# ইউজারের ডাটা স্টোর
user_active_numbers: Dict[int, Dict] = {}
otp_check_tasks: Dict[int, asyncio.Task] = {}
user_country_input: Dict[int, bool] = {}

# টিম কনসোলের লাস্ট OTP ট্র্যাক করার জন্য
last_console_otp_id = None


# ==================== স্টার্ট কমান্ড ====================

async def start_command(update: Update, context: CallbackContext):
    user = update.effective_user
    
    welcome_text = f"""{emoji('✨')} <b>Welcome to Acchub Panel, {user.first_name}!</b> {emoji('✨')}

━━━━━━━━━━━━━━━━━━━━━━━

{emoji('📌')} <b>Features:</b>

• {emoji('📱')} Get virtual numbers
• {emoji('🔑')} Receive OTP instantly
• {emoji('📊')} Track top ranges

━━━━━━━━━━━━━━━━━━━━━━━

<b>Use the buttons below to get started!</b>"""

    await update.message.reply_text(
        welcome_text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )


# ==================== মেসেজ হ্যান্ডলার ====================

async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = update.effective_user.id
    
    # Get Number বাটন
    if text == "Get Number":
        await update.message.reply_text(
            f"{emoji('🌍')} <b>Enter country name:</b>\n\nExample: <code>Tajikistan</code>, <code>Kuwait</code>, <code>Armenia</code>",
            parse_mode="HTML"
        )
        user_country_input[user_id] = True
        return
    
    # Create Season বাটন
    elif text == "Create Season":
        await update.message.reply_text(
            f"{emoji('✨')} <b>Create Season</b>\n\n━━━━━━━━━━━━━━━━━━━━━━━\n\n{emoji('⏳')} <i>This feature is coming soon!</i>\n\nStay tuned for updates! {emoji('🚀')}",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Traffic বাটন
    elif text == "Traffic":
        await update.message.reply_text(
            f"{emoji('📊')} <b>Fetching top OTP ranges...</b>",
            parse_mode="HTML"
        )
        await show_traffic(update, context)
        return
    
    # ইউজার দেশের নাম ইনপুট দিচ্ছে
    if user_country_input.get(user_id, False):
        country_name = text.strip()
        user_country_input[user_id] = False
        
        operators = get_operators_by_country(country_name)
        
        if not operators:
            await update.message.reply_text(
                f"{emoji('❌')} <b>No ranges found for '{country_name}'</b>\n\nPlease try again with correct country name.",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
            return
        
        # দেশের আইডি বের করি
        ranges = load_ranges()
        country_data = ranges.get(country_name, {})
        country_id = country_data.get("country_id")
        
        if not country_id:
            await update.message.reply_text(
                f"{emoji('❌')} <b>Country '{country_name}' not found!</b>\n\nPlease try again.",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
            return
        
        # অপারেটরের লিস্ট স্টোর করি
        context.user_data['current_country_id'] = country_id
        context.user_data['current_operators'] = operators
        context.user_data['current_country_name'] = country_name
        
        # অপারেটর সিলেক্ট কিবোর্ড দেখাই
        await update.message.reply_text(
            f"{emoji('📶')} <b>Select range for {country_name}:</b>",
            parse_mode="HTML",
            reply_markup=get_range_selection_keyboard(operators, country_id)
        )
        return
    
    # অন্য কোনো মেসেজ
    await update.message.reply_text(
        f"{emoji('⚠️')} <b>Please use the buttons below!</b>",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )


# ==================== ট্রাফিক শো ====================

async def show_traffic(update: Update, context: CallbackContext):
    top_ranges = get_top_ranges_from_console()
    
    if not top_ranges:
        traffic_text = f"{emoji('📊')} <b>No OTP data available yet.</b>\n\nTry again later."
    else:
        traffic_lines = []
        for i, (range_name, count) in enumerate(top_ranges, 1):
            traffic_lines.append(f"{i}. <code><b>{range_name}</b></code>\n\n   {emoji('📥')} <code>{count}</code> OTPs\n")
        
        traffic_text = f"""{emoji('🏆')} <b>Top 3 OTP Ranges</b>

━━━━━━━━━━━━━━━━━━━━━━━

{chr(10).join(traffic_lines)}

━━━━━━━━━━━━━━━━━━━━━━━

{emoji('🔄')} <i>Tap refresh to update</i>"""
    
    await update.message.reply_text(
        traffic_text,
        parse_mode="HTML",
        reply_markup=get_traffic_keyboard()
    )


# ==================== কলব্যাক হ্যান্ডলার ====================

async def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    # ========== চেঞ্জ নাম্বার ==========
    if data == "change_number":
        user_data = user_active_numbers.get(user_id, {})
        current_country_id = user_data.get('current_country_id')
        current_operator_id = user_data.get('current_operator_id')
        
        if not current_country_id or not current_operator_id:
            await query.edit_message_text(
                f"{emoji('❌')} <b>No active range found!</b>\n\nPlease select a country first.",
                parse_mode="HTML",
                reply_markup=get_main_keyboard()
            )
            return
        
        await query.edit_message_text(
            f"{emoji('🔄')} <b>Getting new numbers...</b>",
            parse_mode="HTML"
        )
        
        await get_new_numbers_for_user(
            query, user_id, current_country_id, current_operator_id, context
        )
        return
    
    # ========== চেঞ্জ কান্ট্রি ==========
    if data == "change_country":
        user_country_input[user_id] = True
        await query.edit_message_text(
            f"{emoji('🌍')} <b>Enter new country name:</b>\n\nExample: <code>Tajikistan</code>, <code>Kuwait</code>",
            parse_mode="HTML"
        )
        return
    
    # ========== ট্রাফিক রিফ্রেশ ==========
    if data == "refresh_traffic":
        top_ranges = get_top_ranges_from_console()
        
        if not top_ranges:
            traffic_text = f"{emoji('📊')} <b>No OTP data available yet.</b>"
        else:
            traffic_lines = []
            for i, (range_name, count) in enumerate(top_ranges, 1):
                traffic_lines.append(f"{i}. <b>{range_name}</b>\n   {emoji('📥')} <code>{count}</code> OTPs")
            
            traffic_text = f"""{emoji('🏆')} <b>Top 3 OTP Ranges</b>

━━━━━━━━━━━━━━━━━━━━━━━

{chr(10).join(traffic_lines)}

━━━━━━━━━━━━━━━━━━━━━━━

{emoji('🔄')} <i>Tap refresh to update</i>"""
        
        try:
            await query.edit_message_text(
                traffic_text,
                parse_mode="HTML",
                reply_markup=get_traffic_keyboard()
            )
        except BadRequest as e:
            if "Message is not modified" in str(e):
                await query.answer(f"{emoji('📊')} Data is already up to date!", show_alert=False)
            else:
                raise e
        return
    
    # ========== রেঞ্জ সিলেক্ট ==========
    if data.startswith("range_"):
        parts = data.split("_")
        country_id = int(parts[1])
        operator_id = int(parts[2])
        
        operator_name = get_operator_name_by_id(country_id, operator_id)
        country_name = get_country_name_by_id(country_id)
        
        # ইউজারের ডাটা সেভ
        if user_id not in user_active_numbers:
            user_active_numbers[user_id] = {}
        
        user_active_numbers[user_id]['current_country_id'] = country_id
        user_active_numbers[user_id]['current_operator_id'] = operator_id
        user_active_numbers[user_id]['current_operator_name'] = operator_name
        user_active_numbers[user_id]['current_country_name'] = country_name
        
        await query.edit_message_text(
            f"{emoji('🔄')} <b>Getting 3 numbers from</b>\n{emoji('📶')} {operator_name}\n\n{emoji('⏳')} Please wait...",
            parse_mode="HTML"
        )
        
        await get_numbers_for_user(
            query, user_id, country_id, operator_id, operator_name
        )
        return


# ==================== নাম্বার রিকোয়েস্ট ফাংশন ====================

async def get_numbers_for_user(query, user_id: int, country_id: int, operator_id: int, operator_name: str):
    numbers = []
    
    for i in range(3):
        result = request_number(country_id, operator_id)
        if result and result.get("phone_number"):
            numbers.append(result["phone_number"])
        await asyncio.sleep(1)
    
    if len(numbers) == 3:
        # ইউজারের ডাটা সেভ
        user_active_numbers[user_id]['numbers'] = numbers
        user_active_numbers[user_id]['numbers_created_at'] = time.time()
        
        # মেসেজ তৈরি
        message_text = format_user_message(numbers)
        
        # কিবোর্ড তৈরি (কপি বাটন সহ)
        keyboard = get_number_message_keyboard(numbers)
        
        await query.edit_message_text(
            message_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
        # OTP চেকার শুরু
        if user_id in otp_check_tasks:
            otp_check_tasks[user_id].cancel()
        
        otp_check_tasks[user_id] = asyncio.create_task(
            start_otp_checker(user_id, numbers)
        )
    else:
        await query.edit_message_text(
            f"{emoji('❌')} <b>Failed to get numbers!</b>\n\nPlease try again.",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )


async def get_new_numbers_for_user(query, user_id: int, country_id: int, operator_id: int, context):
    numbers = []
    
    for i in range(3):
        result = request_number(country_id, operator_id)
        if result and result.get("phone_number"):
            numbers.append(result["phone_number"])
        await asyncio.sleep(1)
    
    if len(numbers) == 3:
        # আপডেট
        user_active_numbers[user_id]['numbers'] = numbers
        user_active_numbers[user_id]['numbers_created_at'] = time.time()
        
        message_text = format_user_message(numbers)
        keyboard = get_number_message_keyboard(numbers)
        
        await query.edit_message_text(
            message_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
        # OTP চেকার রিস্টার্ট
        if user_id in otp_check_tasks:
            otp_check_tasks[user_id].cancel()
        
        otp_check_tasks[user_id] = asyncio.create_task(
            start_otp_checker(user_id, numbers)
        )
    else:
        await query.edit_message_text(
            f"{emoji('❌')} <b>Failed to get new numbers!</b>\n\nPlease try again.",
            parse_mode="HTML",
            reply_markup=get_main_keyboard()
        )


# ==================== OTP চেকার ====================

async def start_otp_checker(user_id: int, numbers: List[str]):
    sent_otps = set()
    
    while True:
        # মেয়াদ শেষ চেক
        user_data = user_active_numbers.get(user_id, {})
        created_at = user_data.get('numbers_created_at', 0)
        
        if is_number_expired(created_at):
            break
        
        # OTP চেক
        otp_results = check_otp_for_numbers(numbers)
        
        for phone, otp_data in otp_results.items():
            if otp_data and otp_data.get('otp'):
                otp_key = f"{phone}_{otp_data['otp']}"
                
                if otp_key not in sent_otps:
                    sent_otps.add(otp_key)
                    
                    # ইউজারকে OTP পাঠাই
                    await send_otp_to_user(user_id, phone, otp_data)
                    
                    # Otp গ্রুপে পাঠাই
                    await send_otp_to_group(phone, otp_data)
        
        await asyncio.sleep(OTP_CHECK_INTERVAL)


# ==================== OTP পাঠানোর ফাংশন ====================

async def send_otp_to_user(user_id: int, phone: str, otp_data: Dict):
    bot = Bot(token=MAIN_BOT_TOKEN)
    
    message = format_user_otp_message(
        phone=phone,
        otp=otp_data.get('otp', ''),
        service=otp_data.get('service', 'Unknown')
    )
    
    try:
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="HTML"
        )
    except Exception:
        pass


# ==================== Otp Group চেকার (ইউজারের নম্বরের জন্য) ====================

last_otp_group_otp_id = None

async def otp_group_checker():
    """OTP কোড আর কান্ট্রি/রেঞ্জ দুইটাই সমেত Otp Group এ পাঠায়"""
    global last_otp_group_otp_id
    
    while True:
        try:
            otps = get_otp_with_details(100)
            
            if otps:
                latest = otps[0]
                latest_id = f"{latest.get('phone_number')}_{latest.get('otp_code')}"
                
                if latest_id != last_otp_group_otp_id:
                    last_otp_group_otp_id = latest_id
                    
                    phone = latest.get("phone_number", "Unknown")
                    
                    if phone.startswith("+"):
                        hidden_phone = phone[:5] + "*******" + phone[-4:]
                    else:
                        hidden_phone = phone[:4] + "*******" + phone[-4:]
                    
                    message = f"""{emoji('✨')} <b>New OTP Received!</b> {emoji('✨')}

━━━━━━━━━━━━━━━━━━━━━━━

{emoji('📱')} <b>Number:</b> <code>{hidden_phone}</code>

{emoji('🌍')} <b>Country:</b> <code>{latest.get('country_name', 'Unknown')}</code>

{emoji('📶')} <b>Range:</b> <code>{latest.get('operator_name', 'Unknown')}</code>

{get_social_emoji(latest.get('provider', 'WhatsApp'))} <b>Service:</b> {latest.get('provider', 'WhatsApp')}

{emoji('🔑')} <b>OTP:</b> <code>{latest.get('otp_code', 'Unknown')}</code>

━━━━━━━━━━━━━━━━━━━━━━━

{emoji('📝')} <b>Full Message:</b>

{latest.get('sms_text', 'No text')[:200]}

━━━━━━━━━━━━━━━━━━━━━━━

{emoji('💥')} <i>Forwarded from Team X Panel</i>"""
                    
                    bot = Bot(token=FORWARD_BOT_TOKEN)
                    result = await bot.send_message(
                        chat_id=OTP_GROUP_ID,
                        text=message,
                        parse_mode="HTML",
                        reply_markup=get_otp_group_keyboard()
                    )
                    # ৫ মিনিট পর মেসেজ ডিলিট হবে
                    track_message(OTP_GROUP_ID, result.message_id)
                
        except Exception:
            pass
        
        await asyncio.sleep(OTP_CHECK_INTERVAL)


# ==================== টিম কনসোল লাস্ট OTP চেকার (শুধু লাস্ট মেসেজ পাঠাবে) ====================

async def console_otp_checker():
    global last_console_otp_id
    
    while True:
        try:
            console_otps = get_console_team_otps(20)
            
            if console_otps:
                latest_otp = console_otps[0]
                latest_otp_id = latest_otp.get("id")
                
                if latest_otp_id and latest_otp_id != last_console_otp_id:
                    last_console_otp_id = latest_otp_id
                    
                    # পুরো OTP ডাটা পাঠাচ্ছি
                    await send_last_otp_to_range_group(latest_otp)
                
        except Exception:
            pass
        
        await asyncio.sleep(OTP_CHECK_INTERVAL)


async def send_last_otp_to_range_group(otp_data: dict):
    """পুরো OTP ডাটা নিয়ে Range Group এ মেসেজ পাঠায় (নম্বর হাইড করা)"""
    bot = Bot(token=FORWARD_BOT_TOKEN)
    
    country = otp_data.get("country_name", "Unknown")
    range_name = otp_data.get("operator_name", "Unknown")
    service = otp_data.get("provider", "Unknown")
    otp_code = otp_data.get("otp_code", "Unknown")
    sms_text = otp_data.get("sms_text", "No text")
    phone_number = otp_data.get("phone_number", "Unknown")
    
    # নম্বর হাইড করা (শুধু শেষ ৪ ডিজিট দেখাবে)
    if phone_number.startswith("+"):
        hidden_phone = phone_number[:5] + "*******" + phone_number[-4:]
    else:
        hidden_phone = phone_number[:4] + "*******" + phone_number[-4:]
    
    message = f"""{emoji('✨')} <b>New OTP Received!</b> {emoji('✨')}
━━━━━━━━━━━━━━━━━━━━━━━

{emoji('📱')} <b>Number:</b> <code>{hidden_phone}</code>

{emoji('🌍')} <b>Country:</b> <code>{country}</code>

{emoji('📶')} <b>Range:</b> <b><code>{range_name}</code></b>

 <b>Service:</b> {get_social_emoji(service)}

{emoji('🔑')} <b>OTP:</b> <code>{otp_code}</code>
━━━━━━━━━━━━━━━━━━━━━━━
{emoji('📝')} <b>Full Message:</b>

<code>{sms_text}</code>

━━━━━━━━━━━━━━━━━━━━━━━
{emoji('💥')} <i>Forwarded from Team X Panel</i>"""
    
    try:
        result = await bot.send_message(
            chat_id=RANGE_GROUP_ID,
            text=message,
            parse_mode="HTML",
            reply_markup=get_range_group_keyboard()
        )
        # ৫ মিনিট পর মেসেজ ডিলিট হবে
        track_message(RANGE_GROUP_ID, result.message_id)
    except Exception:
        pass


# ==================== send_otp_to_group ফাংশন (যোগ করতে হবে) ====================

async def send_otp_to_group(phone: str, otp_data: Dict):
    """OTP গ্রুপে OTP পাঠানোর ফাংশন"""
    bot = Bot(token=FORWARD_BOT_TOKEN)
    
    hidden_phone = hide_phone_number(phone)
    country = otp_data.get('country_name', 'Unknown')
    range_name = otp_data.get('operator_name', 'Unknown')
    service = otp_data.get('service', 'Unknown')
    otp = otp_data.get('otp', '')
    
    message = f"""{emoji('✨')} <b>New OTP Received!</b> {emoji('✨')}

━━━━━━━━━━━━━━━━━━━━━━━

{emoji('📱')} <b>Number:</b> <code>{hidden_phone}</code>

{emoji('🌍')} <b>Country:</b> <code>{country}</code>

{emoji('📶')} <b>Range:</b> <code>{range_name}</code>

 <b>Service:</b> {get_social_emoji(service)}

{emoji('🔑')} <b>OTP:</b> <code>{otp}</code>

━━━━━━━━━━━━━━━━━━━━━━━

{emoji('💥')} <i>Forwarded from Team X Panel</i>"""
    
    try:
        result = await bot.send_message(
            chat_id=OTP_GROUP_ID,
            text=message,
            parse_mode="HTML",
            reply_markup=get_otp_group_keyboard()
        )
        track_message(OTP_GROUP_ID, result.message_id)
    except Exception:
        pass