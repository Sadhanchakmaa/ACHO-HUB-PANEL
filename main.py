# main.py - বট চালানোর ফাইল

import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from config import MAIN_BOT_TOKEN, FORWARD_BOT_TOKEN
from handlers import (
    start_command,
    handle_message,
    callback_handler,
    show_traffic,
    console_otp_checker,
    otp_group_checker
)
from cleaner import start_auto_cleaner, track_message


async def main():
    print("""
╔══════════════════════════════════╗
║     🤖 Acchub Panel Bot          ║
║     Bot is starting...           ║
╚══════════════════════════════════╝
    """)
    
    # মেইন বট অ্যাপ্লিকেশন
    application = ApplicationBuilder().token(MAIN_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("traffic", show_traffic))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # ফরওয়ার্ড বটের জন্য অটো ক্লিনার শুরু
    await start_auto_cleaner()
    
    # টাস্ক শুরু
    asyncio.create_task(console_otp_checker())
    asyncio.create_task(otp_group_checker())
    
    print("✅ Bot is running! Press Ctrl+C to stop\n")
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopping...")
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


if __name__ == "__main__":
    asyncio.run(main())