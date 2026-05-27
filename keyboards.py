# keyboards.py - সব বাটন তৈরি (কপি বাটন সহ)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, CopyTextButton

from config import (
    NUMBER_BOT_LINK, MAIN_CHANNEL_LINK, OTP_GROUP_LINK, ADMIN_LINK,
    CUSTOM_EMOJI, emoji
)


# ==================== মেইন রিপ্লাই কিবোর্ড ====================

def get_main_keyboard():
    keyboard = [
        [
            KeyboardButton(
                text="Get Number",
                style="success",
                icon_custom_emoji_id=CUSTOM_EMOJI["📱"]
            ),
            KeyboardButton(
                text="Create Season",
                style="primary",
                icon_custom_emoji_id=CUSTOM_EMOJI["✨"]
            )
        ],
        [
            KeyboardButton(
                text="Traffic",
                style="danger",
                icon_custom_emoji_id=CUSTOM_EMOJI["📊"]
            )
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ==================== নাম্বার মেসেজের কিবোর্ড ====================

def get_number_message_keyboard(numbers: list) -> InlineKeyboardMarkup:
    """
    নাম্বার মেসেজের নিচে থাকা কিবোর্ড
    প্রতিটি নাম্বারের জন্য আলাদা কপি বাটন
    """
    keyboard = []
    
    # প্রতিটি নাম্বারের জন্য কপি বাটন
    for num in numbers:
        keyboard.append([
            InlineKeyboardButton(
                text=num,
                copy_text=CopyTextButton(text=num),
            )
        ])
    
    # Change Number, Change Country (এক লাইনে ২টি)
    keyboard.append([
        InlineKeyboardButton(
            text="Change Number",
            style="success",
            icon_custom_emoji_id=CUSTOM_EMOJI["🔄"],
            callback_data="change_number"
        ),
        InlineKeyboardButton(
            text="Change Country",
            style="primary",
            icon_custom_emoji_id=CUSTOM_EMOJI["🌍"],
            callback_data="change_country"
        )
    ])
    
    # Otp Group (আলাদা লাইনে ১টি)
    keyboard.append([
        InlineKeyboardButton(
            text="Otp Group",
            style="danger",
            icon_custom_emoji_id=CUSTOM_EMOJI["🔑"],
            url=OTP_GROUP_LINK
        )
    ])
    
    return InlineKeyboardMarkup(keyboard)


# ==================== ট্রাফিক কিবোর্ড ====================

def get_traffic_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Refresh",
                style="success",
                icon_custom_emoji_id=CUSTOM_EMOJI["🔄"],
                callback_data="refresh_traffic"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== গ্রুপের কিবোর্ড ====================

def get_range_group_keyboard() -> InlineKeyboardMarkup:
    """Range Group এ মেসেজের নিচে থাকা কিবোর্ড"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="Number Bot",
                style="success",
                icon_custom_emoji_id=CUSTOM_EMOJI["🤖"],
                url=NUMBER_BOT_LINK
            ),
            InlineKeyboardButton(
                text="Otp Group",
                style="success",
                icon_custom_emoji_id=CUSTOM_EMOJI["🔑"],
                url=OTP_GROUP_LINK
            )
        ],
        [
            InlineKeyboardButton(
                text="Admin",
                style="primary",
                icon_custom_emoji_id=CUSTOM_EMOJI["👑"],
                url=ADMIN_LINK
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_otp_group_keyboard() -> InlineKeyboardMarkup:
    """Otp Group এ মেসেজের নিচে থাকা কিবোর্ড"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="Number Bot",
                style="success",
                icon_custom_emoji_id=CUSTOM_EMOJI["🤖"],
                url=NUMBER_BOT_LINK
            ),
            InlineKeyboardButton(
                text="Main Channel",
                style="success",
                icon_custom_emoji_id=CUSTOM_EMOJI["📢"],
                url=MAIN_CHANNEL_LINK
            )
        ],
        [
            InlineKeyboardButton(
                text="Admin",
                style="primary",
                icon_custom_emoji_id=CUSTOM_EMOJI["👑"],
                url=ADMIN_LINK
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== রেঞ্জ সিলেক্ট কিবোর্ড ====================

def get_range_selection_keyboard(operators: list, country_id: int) -> InlineKeyboardMarkup:
    """রেঞ্জ সিলেক্ট করার কিবোর্ড"""
    keyboard = []
    
    for operator in operators:
        button = InlineKeyboardButton(
            text=operator["name"],
            callback_data=f"range_{country_id}_{operator['id']}"
        )
        keyboard.append([button])
    
    return InlineKeyboardMarkup(keyboard)