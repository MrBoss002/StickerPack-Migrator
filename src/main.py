import asyncio
import logging
from aiogram import Bot, Dispatcher
from src.config import BOT_TOKEN
from src.handlers.commands import router as commands_router
from src.handlers.conversation import router as conversation_router

async def main():
    # Configure logging to see events in your terminal
    logging.basicConfig(level=logging.INFO)
    
    # Initialize Bot and Dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Register all routers (handlers & conversation wizard)
    dp.include_router(commands_router)
    dp.include_router(conversation_router)

    print("🤖 Sticker-Renamer bot is starting...")
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped successfully!")
