# utils.py - হেলপার ফাংশন (নম্বরের সামনে + যোগ করা হয়েছে)

import requests
import json
import time
from typing import Dict, List, Optional, Tuple

from config import (
    GET_NUMBER_URL, GET_OTP_HISTORY_URL, GET_CONSOLE_TEAM_URL,
    HEADERS, NUMBER_EXPIRY_SECONDS, GET_HISTORY_URL, HIDE_DIGITS_COUNT,
    emoji
)


# ==================== সোশ্যাল মিডিয়া কাস্টম ইমোজি ম্যাপিং ====================

SOCIAL_EMOJI_MAP = {
    "whatsapp": "6210911297182113031",
    "facebook": "6212777627975950308",
    "instagram": "6210636251771444617",
    "telegram": "6212844260098581451",
    "tiktok": "6212813100110846949",
    "discord": "5334595899869905653",
}


def get_social_emoji(service_name: str) -> str:
    """সার্ভিসের নাম অনুযায়ী সোশ্যাল মিডিয়া কাস্টম ইমোজি রিটার্ন করে"""
    if not service_name:
        return emoji("📡")
    
    service_lower = service_name.lower()
    
    # চেক করা কোন সোশ্যাল মিডিয়া ম্যাচ করে
    for key, emoji_id in SOCIAL_EMOJI_MAP.items():
        if key in service_lower:
            return f'<tg-emoji emoji-id="{emoji_id}">💬</tg-emoji>'
    
    # ডিফল্ট ইমোজি
    return emoji("📡")


# ==================== মূল ফাংশন ====================

def load_ranges() -> Dict:
    try:
        with open('ranges.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def get_country_list() -> List[Dict]:
    ranges = load_ranges()
    countries = []
    for country_name, country_data in ranges.items():
        countries.append({
            "name": country_name,
            "country_id": country_data.get("country_id"),
            "country_code": country_data.get("country_code")
        })
    return countries


def get_otp_with_details(limit: int = 100) -> List[Dict]:
    """OTP কোড আর কান্ট্রি/রেঞ্জ দুইটাই একসাথে আনে"""
    try:
        otp_response = requests.get(
            GET_OTP_HISTORY_URL,
            headers=HEADERS,
            timeout=30
        )
        
        history_response = requests.get(
            GET_HISTORY_URL,
            headers=HEADERS,
            timeout=30
        )
        
        otp_dict = {}
        if otp_response.status_code == 200:
            otp_data = otp_response.json().get("otp-history", {}).get("data", [])
            for otp in otp_data:
                phone = otp.get("phone_number", "")
                otp_dict[phone] = {
                    "otp": otp.get("otp_code", ""),
                    "service": otp.get("provider", "Unknown"),
                    "sms_text": otp.get("sms_text", "")
                }
        
        result = []
        if history_response.status_code == 200:
            history_data = history_response.json().get("history", {}).get("data", [])
            for item in history_data:
                phone = item.get("phone_number", "")
                if not phone.startswith("+"):
                    phone = f"+{phone}"
                
                if phone in otp_dict:
                    result.append({
                        "phone_number": phone,
                        "otp_code": otp_dict[phone]["otp"],
                        "provider": otp_dict[phone]["service"],
                        "sms_text": otp_dict[phone]["sms_text"],
                        "country_name": item.get("country_name", "Unknown"),
                        "operator_name": item.get("operator_name", "Unknown"),
                        "status": item.get("status", "unknown")
                    })
        
        return result[:limit]
        
    except Exception:
        return []


def get_country_from_phone(phone: str) -> str:
    """ফোন নম্বর থেকে কান্ট্রি নাম বের করে"""
    ranges = load_ranges()
    for country_name, country_data in ranges.items():
        country_code = country_data.get("country_code", "")
        if phone.startswith(f"+{country_code}") or phone.startswith(country_code):
            return country_name
    return "Unknown"


def get_operators_by_country(country_name: str) -> List[Dict]:
    ranges = load_ranges()
    country_data = ranges.get(country_name, {})
    return country_data.get("operators", [])


def get_operator_name_by_id(country_id: int, operator_id: int) -> str:
    ranges = load_ranges()
    for country_name, country_data in ranges.items():
        if country_data.get("country_id") == country_id:
            for op in country_data.get("operators", []):
                if op.get("id") == operator_id:
                    return op.get("name", "")
    return ""


def get_country_name_by_id(country_id: int) -> str:
    ranges = load_ranges()
    for country_name, country_data in ranges.items():
        if country_data.get("country_id") == country_id:
            return country_name
    return ""


def format_phone_number(phone: str) -> str:
    """ফোন নম্বরের সামনে + যোগ করে"""
    if not phone:
        return phone
    
    phone = str(phone).strip()
    
    # যদি ইতিমধ্যে + থাকে তাহলে ফেরত দিন
    if phone.startswith("+"):
        return phone
    
    # যদি 0 বা 00 দিয়ে শুরু হয় তাহলে সেটা বাদ দিন
    if phone.startswith("00"):
        phone = phone[2:]
    elif phone.startswith("0"):
        phone = phone[1:]
    
    # API থেকে আসা নম্বর সাধারণত কান্ট্রি কোড সহ ই আসে
    return f"+{phone}"


def request_number(country_id: int, operator_id: int) -> Optional[Dict]:
    payload = {
        "country_id": country_id,
        "operator_id": operator_id,
        "number_format": "full"
    }
    
    try:
        response = requests.post(
            GET_NUMBER_URL,
            headers=HEADERS,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 201:
            data = response.json()
            result = data.get("data", {})
            # নম্বর ফরম্যাট করে দিচ্ছি
            if result and result.get("phone_number"):
                result["phone_number"] = format_phone_number(result["phone_number"])
            return result
        else:
            return None
            
    except Exception:
        return None


def check_otp_for_numbers(phone_numbers: List[str]) -> Dict[str, Optional[Dict]]:
    result = {}
    
    try:
        response = requests.get(
            GET_OTP_HISTORY_URL,
            headers=HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            otp_history = data.get("otp-history", {}).get("data", [])
            
            for otp_record in otp_history:
                phone = otp_record.get("phone_number", "")
                clean_phone = phone.replace("+", "")
                
                for target_phone in phone_numbers:
                    target_clean = target_phone.replace("+", "")
                    if target_clean == clean_phone or target_clean in phone:
                        result[target_phone] = {
                            "otp": otp_record.get("otp_code", ""),
                            "service": otp_record.get("provider", "Unknown"),
                            "country_name": otp_record.get("country_name"),
                            "operator_name": otp_record.get("operator_name")
                        }
                        break
                        
    except Exception:
        pass
    
    return result


def get_console_team_otps(limit: int = 100) -> List[Dict]:
    try:
        response = requests.get(
            GET_CONSOLE_TEAM_URL,
            headers=HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("data", [])[:limit]
        else:
            return []
            
    except Exception:
        return []


def get_otp_history(limit: int = 100) -> List[Dict]:
    """OTP হিস্ট্রি থেকে লিমিট অনুযায়ী ডাটা আনে"""
    try:
        response = requests.get(
            GET_OTP_HISTORY_URL,
            headers=HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            otp_history = data.get("otp-history", {}).get("data", [])
            return otp_history[:limit]
        else:
            return []
            
    except Exception:
        return []


def get_top_ranges_from_console() -> List[Tuple[str, int]]:
    otps = get_console_team_otps(100)
    range_count = {}
    
    for otp in otps:
        operator_name = otp.get("operator_name")
        if operator_name:
            range_count[operator_name] = range_count.get(operator_name, 0) + 1
    
    sorted_ranges = sorted(range_count.items(), key=lambda x: x[1], reverse=True)
    return sorted_ranges[:3]


def hide_phone_number(phone: str) -> str:
    if not phone:
        return phone
    
    clean = phone.replace("+", "")
    if len(clean) <= HIDE_DIGITS_COUNT:
        return phone
    
    visible_part = clean[-HIDE_DIGITS_COUNT:]
    hide_part = "*" * (len(clean) - HIDE_DIGITS_COUNT)
    
    if phone.startswith("+"):
        return f"+{hide_part}{visible_part}"
    else:
        return f"{hide_part}{visible_part}"


def format_user_message(numbers: List[str]) -> str:
    num_lines = []
    for i, num in enumerate(numbers, 1):
        # নম্বর ফরম্যাট করা (ইতিমধ্যে + আছে, তবুও নিশ্চিত করছি)
        if not num.startswith("+"):
            num = f"+{num}"
        num_lines.append(f"{emoji('📱')} <b>Number {i}:</b> <code>{num}</code>")
    
    num_text = "\n".join(num_lines)
    
    return f"""{emoji('✅')} <b>Success! 3 Numbers Allocated Done!</b>

━━━━━━━━━━━━━━━━━━━━━━━

{num_text}

━━━━━━━━━━━━━━━━━━━━━━━

{emoji('⏳')} <b>Waiting for OTP...</b>"""


def format_otp_group_message(phone: str, otp: str, service: str, country: str, range_name: str) -> str:
    hidden_phone = hide_phone_number(phone)
    service_icon = get_social_emoji(service)  # ← সোশ্যাল ইমোজি যোগ করা হয়েছে
    return f"""{emoji('📱')} <b>Number:</b> <code>{hidden_phone}</code>
{emoji('🔑')} <b>Otp:</b> <code>{otp}</code>
{service_icon} <b>Service:</b> {service}
{emoji('🌍')} <b>Country:</b> {country}
{emoji('📶')} <b>Range:</b> {range_name}"""


def format_user_otp_message(phone: str, otp: str, service: str) -> str:
    # ইউজারের OTP মেসেজে নম্বর ফরম্যাট করা
    if not phone.startswith("+"):
        phone = f"+{phone}"
    service_icon = get_social_emoji(service)  # ← সোশ্যাল ইমোজি যোগ করা হয়েছে
    return f"""{emoji('📱')} <b>Phone number:</b> <code>{phone}</code>
{emoji('🔑')} <b>Otp:</b> <code>{otp}</code>
{service_icon} <b>Service:</b> {service}"""


def format_range_group_message(country: str, range_name: str, service: str) -> str:
    service_icon = get_social_emoji(service)  # ← সোশ্যাল ইমোজি যোগ করা হয়েছে
    return f"""{emoji('🌍')} <b>Country:</b> {country}
{emoji('📶')} <b>Range:</b> {range_name}
{service_icon} <b>Service:</b> {service}"""


def is_number_expired(created_at: float) -> bool:
    return time.time() - created_at > NUMBER_EXPIRY_SECONDS