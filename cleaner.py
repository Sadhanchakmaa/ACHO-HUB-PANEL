# cleaner.py - মেসেজ অটো ডিলিট মডিউল (প্রিন্ট ছাড়া)

import asyncio
from telegram import Bot
from telegram.error import BadRequest
from config import FORWARD_BOT_TOKEN

DELETE_AFTER_SECONDS = 180
messages_to_delete = {}


async def start_auto_cleaner():
    asyncio.create_task(delete_expired_messages())


async def delete_expired_messages():
    bot = Bot(token=FORWARD_BOT_TOKEN)
    
    while True:
        try:
            current_time = asyncio.get_event_loop().time()
            
            for chat_id, messages in list(messages_to_delete.items()):
                for msg in messages[:]:
                    if msg["delete_at"] <= current_time:
                        try:
                            await bot.delete_message(
                                chat_id=chat_id,
                                message_id=msg["message_id"]
                            )
                        except BadRequest:
                            pass
                        messages.remove(msg)
                
                if not messages_to_delete[chat_id]:
                    del messages_to_delete[chat_id]
                    
        except Exception:
            pass
        
        await asyncio.sleep(1)


def track_message(chat_id: int, message_id: int):
    current_time = asyncio.get_event_loop().time()
    delete_at = current_time + DELETE_AFTER_SECONDS
    
    if chat_id not in messages_to_delete:
        messages_to_delete[chat_id] = []
    
    messages_to_delete[chat_id].append({
        "message_id": message_id,
        "delete_at": delete_at
    })